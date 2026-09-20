import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import { MaterialIcon, Avatar } from '../components/ui';
import TopAppBar from '../components/layout/TopAppBar';
import Toast from '../components/Toast';
import { formatDate, titleCase } from '../utils/format';

const tabs = [
  { id: 'overview', label: 'Overview', icon: 'dashboard' },
  { id: 'ngos', label: 'NGO Verification', icon: 'workspace_premium' },
  { id: 'users', label: 'Users', icon: 'group' },
];

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [summary, setSummary] = useState(null);
  const [pendingNgos, setPendingNgos] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [toast, setToast] = useState(null);
  const [busy, setBusy] = useState(null);

  const showToast = (message, tone = 'success') => {
    setToast({ message, tone });
    setTimeout(() => setToast(null), 3500);
  };

  const loadOverview = useCallback(async () => {
    try {
      const res = await api.get('/analytics/summary');
      setSummary(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load analytics');
    }
  }, []);

  const loadNgos = useCallback(async () => {
    try {
      const res = await api.get('/admin/ngos/pending');
      setPendingNgos(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load NGOs');
    }
  }, []);

  const loadUsers = useCallback(async () => {
    try {
      const res = await api.get('/admin/users');
      setUsers(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load users');
    }
  }, []);

  const loadTab = useCallback(async () => {
    setError('');
    setLoading(true);
    await Promise.all([loadOverview(), loadNgos(), loadUsers()]);
    setLoading(false);
  }, [loadOverview, loadNgos, loadUsers]);

  useEffect(() => {
    loadTab(activeTab);
  }, [activeTab, loadTab]);

  const decideNgo = async (id, approve, profile) => {
    setBusy(`verify-${id}-${approve}`);
    try {
      await api.patch(`/admin/ngos/${id}/verify`, null, { params: { approve } });
      showToast(approve ? `${profile?.name || 'NGO'} verified` : 'Verification rejected');
      loadNgos();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Action failed', 'error');
    } finally {
      setBusy(null);
    }
  };

  const changeRole = async (userId, newRole) => {
    setBusy(`role-${userId}`);
    try {
      await api.patch(`/admin/users/${userId}/role`, null, { params: { new_role: newRole } });
      showToast('Role updated');
      loadUsers();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Could not update role', 'error');
    } finally {
      setBusy(null);
    }
  };

  const categoryEntries = Object.entries(summary?.by_category || {});
  const categoryMax = Math.max(1, ...categoryEntries.map(([, v]) => v));

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface antialiased">
      <TopAppBar subtitle="Admin" />
      <main className="w-full max-w-6xl mx-auto px-margin-mobile pt-20 pb-16 space-y-6">
        <header className="flex flex-col gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-tertiary-container text-on-tertiary-container flex items-center justify-center">
              <MaterialIcon name="admin_panel_settings" size={26} />
            </div>
            <div>
              <h1 className="font-headline-lg text-headline-lg text-on-surface">Admin Console</h1>
              <p className="font-body-sm text-on-surface-variant">Platform analytics, NGO verification, and user management</p>
            </div>
          </div>
          <nav className="flex items-center gap-2 overflow-x-auto no-scrollbar">
            {tabs.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setActiveTab(t.id)}
                className={`px-4 py-2 rounded-full font-label-md flex items-center gap-1.5 transition-colors shrink-0 ${
                  activeTab === t.id ? 'bg-primary text-on-primary' : 'bg-surface-container-low text-on-surface-variant hover:text-on-surface'
                }`}
              >
                <MaterialIcon name={t.icon} size={18} />
                {t.label}
              </button>
            ))}
          </nav>
        </header>

        {error && (
          <div className="bg-error-container text-on-error-container rounded-lg p-4 font-body-sm flex items-center gap-2">
            <MaterialIcon name="error" size={18} />
            <span className="flex-1">{error}</span>
            <button type="button" onClick={() => setError('')} aria-label="Dismiss"><MaterialIcon name="close" size={18} /></button>
          </div>
        )}

        {loading && activeTab === 'overview' ? (
          <div className="flex items-center justify-center h-48 text-on-surface-variant">Loading analytics...</div>
        ) : activeTab === 'overview' && summary ? (
          <>
            <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <div className="bg-tertiary-container rounded-lg p-4 flex flex-col gap-1">
                <span className="font-display text-display-lg text-on-tertiary-container">{summary.total_items_redistributed}</span>
                <span className="font-label-sm text-on-tertiary-container">Items Redistributed</span>
              </div>
              <div className="bg-primary-container rounded-lg p-4 flex flex-col gap-1">
                <span className="font-display text-display-lg text-on-primary-container">
                  {summary.avg_time_match_to_delivery_hours != null ? `${Math.round(summary.avg_time_match_to_delivery_hours)}h` : '—'}
                </span>
                <span className="font-label-sm text-on-primary-container">Avg Match → Delivery</span>
              </div>
              <div className="bg-secondary-container rounded-lg p-4 flex flex-col gap-1">
                <span className="font-display text-display-lg text-on-secondary-container">{summary.unmet_requests}</span>
                <span className="font-label-sm text-on-secondary-container">Unmet Requests (30d+)</span>
              </div>
              <div className="bg-surface-container-high rounded-lg p-4 flex flex-col gap-1">
                <span className="font-display text-display-lg text-on-surface">{pendingNgos.length}</span>
                <span className="font-label-sm text-on-surface-variant">NGOs Awaiting Review</span>
              </div>
            </section>

            <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-5">
              <div className="flex items-center gap-1.5 mb-4">
                <MaterialIcon name="category" size={20} className="text-primary" />
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Redistribution by Category</h3>
              </div>
              {categoryEntries.length === 0 ? (
                <p className="py-6 text-center font-body-sm text-on-surface-variant">No redistributed items yet</p>
              ) : (
                <div className="flex flex-col gap-3">
                  {categoryEntries.map(([cat, total]) => (
                    <div key={cat} className="flex flex-col gap-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-label-md text-on-surface capitalize">{cat}</span>
                        <span className="font-label-md text-on-surface-variant">{total}</span>
                      </div>
                      <div className="h-2.5 rounded-full bg-surface-container-high overflow-hidden">
                        <div className="h-full rounded-full bg-tertiary" style={{ width: `${(total / categoryMax) * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 overflow-hidden">
              <div className="px-5 py-4 flex items-center gap-1.5">
                <MaterialIcon name="workspace_premium" size={20} className="text-primary" />
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Top NGOs by Accepted Matches</h3>
              </div>
              {summary.top_ngos.length === 0 ? (
                <p className="px-5 py-8 text-center font-body-sm text-on-surface-variant">No accepted matches yet</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left font-body-sm">
                    <thead>
                      <tr className="bg-surface-container-low text-on-surface-variant font-label-md">
                        <th className="px-5 py-3 font-label-md">NGO</th>
                        <th className="px-4 py-3 font-label-md">Matches</th>
                        <th className="px-4 py-3 font-label-md">Avg Score</th>
                        <th className="px-5 py-3 font-label-md">Reliability</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.top_ngos.map((n) => (
                        <tr key={n.ngo_id} className="border-t border-outline-variant/20">
                          <td className="px-5 py-3 font-label-md text-on-surface">{n.name}</td>
                          <td className="px-4 py-3 text-on-surface">{n.matches_count}</td>
                          <td className="px-4 py-3 text-on-surface">{Math.round((n.avg_score || 0) * 100)}%</td>
                          <td className="px-5 py-3">
                            <span className="chip bg-tertiary-container text-on-tertiary-container">{n.reliability_score?.toFixed(1)}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            {summary.monthly_trend.length > 0 && (
              <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-5">
                <div className="flex items-center gap-1.5 mb-4">
                  <MaterialIcon name="show_chart" size={20} className="text-primary" />
                  <h3 className="font-headline-sm text-headline-sm text-on-surface">12-Month Delivery Trend</h3>
                </div>
                <div className="flex items-end gap-2 h-40">
                  {summary.monthly_trend.map((m) => {
                    const max = Math.max(1, ...summary.monthly_trend.map((x) => x.quantity || 0));
                    return (
                      <div key={m.month} className="flex-1 flex flex-col items-center gap-1 min-w-0">
                        <div className="w-full rounded-t-lg bg-tertiary-container" style={{ height: `${Math.max(4, ((m.quantity || 0) / max) * 100)}%`, minHeight: 4 }} title={`${m.month}: ${m.quantity}`} />
                        <span className="font-label-sm text-on-surface-variant text-[10px] truncate">{m.month.slice(5)}</span>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}
          </>
        ) : activeTab === 'ngos' ? (
          <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 overflow-hidden">
            <div className="px-5 py-4">
              <h3 className="font-headline-sm text-headline-sm text-on-surface">Pending NGO Verification</h3>
              <p className="font-body-sm text-on-surface-variant mt-1">Nonprofits that submitted profiles and await approval</p>
            </div>
            {pendingNgos.length === 0 ? (
              <p className="px-5 py-10 text-center font-body-sm text-on-surface-variant">
                No NGOs waiting for review
              </p>
            ) : (
              <div className="flex flex-col">
                {pendingNgos.map((p) => (
                  <div key={p.id} className="flex flex-col md:flex-row md:items-center gap-3 px-5 py-4 border-t border-outline-variant/20">
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <Avatar name={p.name || `NGO #${p.id}`} size={40} />
                      <div className="min-w-0">
                        <p className="font-label-lg text-on-surface truncate">{p.name}</p>
                        <p className="font-label-sm text-on-surface-variant truncate">{p.reg_number}</p>
                        <div className="flex gap-1.5 mt-1 flex-wrap">
                          {p.focus_areas?.slice(0, 3).map((a) => (
                            <span key={a} className="chip bg-surface-container-high text-on-surface-variant">{a}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        type="button"
                        disabled={busy === `verify-${p.id}-false`}
                        onClick={() => decideNgo(p.id, false, p)}
                        className="btn-outline px-4 py-2 text-error"
                      >
                        Reject
                      </button>
                      <button
                        type="button"
                        disabled={busy === `verify-${p.id}-true`}
                        onClick={() => decideNgo(p.id, true, p)}
                        className="btn-primary px-4 py-2"
                      >
                        Verify
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        ) : activeTab === 'users' ? (
          <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 overflow-hidden">
            <div className="px-5 py-4">
              <h3 className="font-headline-sm text-headline-sm text-on-surface">All Users</h3>
              <p className="font-body-sm text-on-surface-variant mt-1">{users.length} registered accounts</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left font-body-sm">
                <thead>
                  <tr className="bg-surface-container-low text-on-surface-variant font-label-md">
                    <th className="px-5 py-3 font-label-md">User</th>
                    <th className="px-4 py-3 font-label-md">Role</th>
                    <th className="px-4 py-3 font-label-md">Verified</th>
                    <th className="px-4 py-3 font-label-md">Joined</th>
                    <th className="px-5 py-3 font-label-md">Change Role</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-t border-outline-variant/20">
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-3">
                          <Avatar name={u.name} size={34} />
                          <div className="min-w-0">
                            <p className="font-label-md text-on-surface truncate">{u.name}</p>
                            <p className="font-label-sm text-on-surface-variant truncate">{u.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`chip ${u.role === 'ngo' ? 'bg-secondary-container text-on-secondary-container' : 'bg-surface-container-high text-on-surface-variant'}`}>
                          {titleCase(u.role)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {u.verified ? (
                          <span className="chip bg-tertiary-container text-on-tertiary-container">
                            <MaterialIcon name="check_circle" size={14} /> Verified
                          </span>
                        ) : (
                          <span className="chip bg-surface-container-high text-on-surface-variant">Pending</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-on-surface-variant">{formatDate(u.created_at)}</td>
                      <td className="px-5 py-3">
                        <select
                          className="field py-1.5 text-sm"
                          value={u.role}
                          disabled={busy === `role-${u.id}`}
                          onChange={(e) => changeRole(u.id, e.target.value)}
                        >
                          {['donor', 'ngo', 'volunteer', 'admin'].map((r) => (
                            <option key={r} value={r}>{titleCase(r)}</option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : (
          <div className="flex items-center justify-center h-48 text-on-surface-variant">Loading...</div>
        )}
      </main>

      <Toast message={toast?.message} tone={toast?.tone} onClose={() => setToast(null)} />
    </div>
  );
}