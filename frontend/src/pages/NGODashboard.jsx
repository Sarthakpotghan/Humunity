import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { MaterialIcon, Avatar, StatusBadge } from '../components/ui';
import TopAppBar from '../components/layout/TopAppBar';
import Toast from '../components/Toast';
import {
  formatDate,
  formatDateTime,
  daysUntil,
  titleCase,
  categoryIcon,
  categoryLabel,
} from '../utils/format';

const initialForm = {
  category: 'clothes',
  item_type: '',
  size: '',
  age_group: '',
  gender: 'unisex',
  season: '',
  quantity_needed: 1,
  urgency: 3,
  beneficiary_group: '',
  deadline: '',
};

const statusFilters = ['all', 'active', 'fulfilled', 'closed'];

export default function NGODashboard() {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');

  const loadAll = useCallback(async () => {
    try {
      const [reqRes, profileRes] = await Promise.all([
        api.get('/requests'),
        api.get('/auth/ngo/profile').catch(() => null),
      ]);
      setRequests(reqRes.data || []);
      setProfile(profileRes?.data || null);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load NGO data');
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const showToast = (message, tone = 'success') => {
    setToast({ message, tone });
    setTimeout(() => setToast(null), 3500);
  };

  const activeNeeds = requests.filter((r) => r.status === 'active');
  const fulfilled = requests.filter((r) => r.status === 'fulfilled');
  const filtered = activeFilter === 'all'
    ? requests
    : requests.filter((r) => r.status === activeFilter);

  const stats = [
    { label: 'Active Ground Needs', value: activeNeeds.length, icon: 'campaign', tone: 'tertiary' },
    { label: 'Fulfilled Needs', value: fulfilled.length, icon: 'task_alt', tone: 'primary' },
    { label: 'Total Requests', value: requests.length, icon: 'inventory_2', tone: 'secondary' },
  ];

  const submitRequest = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...form,
        quantity_needed: parseInt(form.quantity_needed, 10),
        urgency: parseInt(form.urgency, 10),
        deadline: form.deadline ? new Date(form.deadline).toISOString() : undefined,
      };
      Object.keys(payload).forEach((key) => {
        if (payload[key] === '' || payload[key] === null || payload[key] === undefined) {
          delete payload[key];
        }
      });
      await api.post('/requests', payload);
      setShowCreate(false);
      setForm(initialForm);
      showToast('Resource need published successfully');
      loadAll();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to publish request', 'error');
    } finally {
      setSaving(false);
    }
  };

  const deadlineText = (req) => {
    const days = daysUntil(req.deadline);
    if (days === null) return null;
    if (days < 0) return { label: `Overdue by ${Math.abs(days)}d`, tone: 'error' };
    if (days === 0) return { label: 'Due today', tone: 'error' };
    return { label: `Due in ${days}d`, tone: days <= 2 ? 'error' : 'neutral' };
  };

  const urgencyBadge = (urgency) => {
    const tones = {
      5: 'bg-error-container text-on-error-container',
      4: 'bg-secondary-fixed text-on-secondary-fixed-variant',
      3: 'bg-secondary-container text-on-secondary-container',
    };
    return tones[urgency] || 'bg-surface-container-high text-on-surface-variant';
  };

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface antialiased">
      <TopAppBar subtitle="NGO Dashboard" />
      <main className="w-full max-w-6xl mx-auto px-margin-mobile pt-20 pb-24 space-y-6">

        <header className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-5 flex flex-col md:flex-row md:items-center gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <Avatar name={user?.name} size={56} />
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="font-headline-md text-headline-md text-on-surface truncate">{user?.name}</h1>
                {profile ? (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-tertiary-container text-on-tertiary-container font-label-sm font-bold">
                    <MaterialIcon name="verified" size={14} fill={1} />
                    Verified NGO
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant font-label-sm font-bold">
                    <MaterialIcon name="hourglass_empty" size={14} />
                    Verification Pending
                  </span>
                )}
              </div>
              <p className="font-body-sm text-on-surface-variant truncate">{user?.email}</p>
              <div className="flex items-center gap-2 flex-wrap mt-1.5">
                {profile?.reg_number && (
                  <span className="font-label-sm text-on-surface-variant">{profile.reg_number}</span>
                )}
                {profile?.focus_areas?.map((area) => (
                  <span key={area} className="chip bg-surface-container-high text-on-surface-variant">
                    {area}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 md:ml-auto">
            {profile && (
              <div className="flex items-center gap-1.5 px-3 py-2 rounded-full bg-primary-container/60 text-on-primary-container font-label-md">
                <MaterialIcon name="workspace_premium" size={18} />
                <span className="font-bold">{profile.reliability_score?.toFixed(1)}</span>
                <span className="font-label-sm">reliability</span>
              </div>
            )}
            <button type="button" onClick={() => setShowCreate(true)} className="btn-primary">
              <MaterialIcon name="add" size={20} />
              Post New Resource Need
            </button>
          </div>
        </header>

        {!profile && (
          <div className="bg-surface-container-low rounded-lg p-4 flex items-center gap-3 border border-outline-variant/30">
            <MaterialIcon name="info" size={22} className="text-on-surface-variant" />
            <p className="font-body-sm text-on-surface-variant">
              Your NGO profile is not set up yet. An admin needs to verify your registration before you can receive matches.
            </p>
          </div>
        )}

        {error && (
          <div className="bg-error-container text-on-error-container rounded-lg p-4 font-body-sm">
            {error}
          </div>
        )}

        <section className="grid grid-cols-3 gap-3">
          {stats.map((s) => (
            <div key={s.label} className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-4 flex flex-col gap-2">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${s.tone === 'tertiary' ? 'bg-tertiary-container text-on-tertiary-container' : s.tone === 'primary' ? 'bg-primary-container text-on-primary-container' : 'bg-secondary-container text-on-secondary-container'}`}>
                <MaterialIcon name={s.icon} size={22} />
              </div>
              <span className="font-display text-display-lg text-on-surface">{s.value}</span>
              <span className="font-label-sm text-on-surface-variant">{s.label}</span>
            </div>
          ))}
        </section>

        <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 overflow-hidden">
          <div className="px-5 pt-5 pb-3 flex items-center justify-between flex-wrap gap-2">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">Active Needs &amp; Incoming Matches</h2>
            {requests.length > 0 && (
              <span className="chip bg-surface-container-high text-on-surface-variant">{requests.length} total</span>
            )}
          </div>
          {activeNeeds.length === 0 ? (
            <div className="px-5 py-10 text-center">
              <MaterialIcon name="campaign" size={40} className="text-outline mx-auto mb-3" />
              <p className="font-body-md text-on-surface-variant">No active needs right now</p>
              <button type="button" onClick={() => setShowCreate(true)} className="btn-tonal mt-4">
                <MaterialIcon name="add" size={18} /> Post your first need
              </button>
            </div>
          ) : (
            <div className="px-5 pb-5 grid grid-cols-1 md:grid-cols-2 gap-4">
              {activeNeeds.map((req) => {
                const dl = deadlineText(req);
                return (
                  <article key={req.id} className="bg-surface-container-low rounded-lg p-4 flex flex-col gap-3">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 rounded-full bg-primary-container/50 text-on-primary-container flex items-center justify-center shrink-0">
                        <MaterialIcon name={categoryIcon(req.category)} size={22} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-headline-sm text-headline-sm text-on-surface truncate capitalize">{req.item_type}</p>
                        <p className="font-label-sm text-on-surface-variant">{categoryLabel(req.category)}</p>
                      </div>
                      <StatusBadge status={req.status} size="sm" showDot={req.status === 'active'} />
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="chip bg-surface-container-highest text-on-surface-variant">
                        <MaterialIcon name="workspaces" size={15} /> Qty {req.quantity_needed}
                      </span>
                      {req.urgency && (
                        <span className={`chip ${urgencyBadge(req.urgency)}`}>
                          <MaterialIcon name="priority_high" size={15} /> Urgency {req.urgency}/5
                        </span>
                      )}
                      {req.beneficiary_group && (
                        <span className="chip bg-surface-container-highest text-on-surface-variant">
                          <MaterialIcon name="groups" size={15} /> {req.beneficiary_group}
                        </span>
                      )}
                      {dl && (
                        <span className={`chip ${dl.tone === 'error' ? 'bg-error-container text-on-error-container' : 'bg-secondary-container text-on-secondary-container'}`}>
                          <MaterialIcon name="schedule" size={15} /> {dl.label}
                        </span>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2 text-body-sm text-on-surface-variant">
                      {[req.age_group, req.gender, req.season].filter(Boolean).map((f) => (
                        <span key={f} className="capitalize">• {f}</span>
                      ))}
                      <span>• Listed {formatDate(req.created_at)}</span>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>

        <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 overflow-hidden">
          <div className="px-5 pt-5 pb-3 flex items-center justify-between flex-wrap gap-2">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">Request History</h2>
            <div className="flex items-center gap-1.5">
              {statusFilters.map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => setActiveFilter(f)}
                  className={`px-3 py-1.5 rounded-full font-label-md transition-colors ${
                    activeFilter === f
                      ? 'bg-primary text-on-primary'
                      : 'bg-surface-container-low text-on-surface-variant hover:text-on-surface'
                  }`}
                >
                  {f === 'all' ? 'All' : titleCase(f)}
                </button>
              ))}
            </div>
          </div>
          {filtered.length === 0 ? (
            <div className="px-5 py-10 text-center text-on-surface-variant">
              No requests match this filter
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left font-body-sm">
                <thead>
                  <tr className="bg-surface-container-low text-on-surface-variant font-label-md">
                    <th className="px-5 py-3 font-label-md">Need</th>
                    <th className="px-4 py-3 font-label-md">Beneficiary</th>
                    <th className="px-4 py-3 font-label-md">Qty</th>
                    <th className="px-4 py-3 font-label-md">Urgency</th>
                    <th className="px-4 py-3 font-label-md">Deadline</th>
                    <th className="px-4 py-3 font-label-md">Status</th>
                    <th className="px-5 py-3 font-label-md">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((req) => {
                    const dl = deadlineText(req);
                    return (
                      <tr key={req.id} className="border-t border-outline-variant/20 hover:bg-surface-container-low/60">
                        <td className="px-5 py-3">
                          <span className="font-label-lg text-on-surface capitalize">{req.item_type}</span>
                          <span className="block font-label-sm text-on-surface-variant">{categoryLabel(req.category)}</span>
                        </td>
                        <td className="px-4 py-3 text-on-surface-variant">{req.beneficiary_group || '—'}</td>
                        <td className="px-4 py-3 text-on-surface font-bold">{req.quantity_needed}</td>
                        <td className="px-4 py-3">
                          {req.urgency ? (
                            <span className={`px-2 py-0.5 rounded-full font-label-sm font-bold ${urgencyBadge(req.urgency)}`}>
                              {req.urgency}
                            </span>
                          ) : '—'}
                        </td>
                        <td className="px-4 py-3 text-on-surface-variant">
                          {dl ? (
                            <span className={dl.tone === 'error' ? 'text-error font-bold' : ''}>{dl.label}</span>
                          ) : '—'}
                        </td>
                        <td className="px-4 py-3"><StatusBadge status={req.status} size="sm" /></td>
                        <td className="px-5 py-3 text-on-surface-variant">{formatDateTime(req.created_at)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      {showCreate && (
        <div className="fixed inset-0 z-[90] bg-black/40 flex items-end md:items-center justify-center p-0 md:p-6" onClick={() => setShowCreate(false)}>
          <div
            className="bg-surface-container-lowest w-full md:max-w-2xl rounded-t-3xl md:rounded-lg max-h-[92dvh] overflow-y-auto no-scrollbar p-6 shadow-elevated animate-fade-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-headline-md text-headline-md text-on-surface">Post New Resource Need</h3>
              <button type="button" className="icon-btn" onClick={() => setShowCreate(false)} aria-label="Close">
                <MaterialIcon name="close" size={22} />
              </button>
            </div>
            <form onSubmit={submitRequest} className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {['clothes', 'stationery'].map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setForm({ ...form, category: cat })}
                    className={`rounded-full py-2.5 px-4 font-label-md flex items-center justify-center gap-1.5 ${
                      form.category === cat ? 'bg-tertiary-container text-on-tertiary-container' : 'bg-surface-container-low text-on-surface-variant'
                    }`}
                  >
                    <MaterialIcon name={categoryIcon(cat)} size={18} />
                    {categoryLabel(cat)}
                  </button>
                ))}
                <div className="col-span-2 md:col-span-2">
                  <label className="block font-label-md text-on-surface-variant mb-1">Item Type *</label>
                  <input required className="field" placeholder="e.g., warm jackets" value={form.item_type} onChange={(e) => setForm({ ...form, item_type: e.target.value })} />
                </div>
                <div>
                  <label className="block font-label-md text-on-surface-variant mb-1">Quantity Needed *</label>
                  <input required type="number" min="1" className="field" value={form.quantity_needed} onChange={(e) => setForm({ ...form, quantity_needed: e.target.value })} />
                </div>
                <div>
                  <label className="block font-label-md text-on-surface-variant mb-1">Beneficiary Group</label>
                  <input className="field" placeholder="e.g., school children" value={form.beneficiary_group} onChange={(e) => setForm({ ...form, beneficiary_group: e.target.value })} />
                </div>
                <div>
                  <label className="block font-label-md text-on-surface-variant mb-1">Age Group</label>
                  <input className="field" placeholder="e.g., 6-10" value={form.age_group} onChange={(e) => setForm({ ...form, age_group: e.target.value })} />
                </div>
                <div>
                  <label className="block font-label-md text-on-surface-variant mb-1">Gender</label>
                  <select className="field" value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })}>
                    {['unisex', 'male', 'female'].map((g) => <option key={g} value={g}>{titleCase(g)}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block font-label-md text-on-surface-variant mb-1">Season</label>
                  <select className="field" value={form.season} onChange={(e) => setForm({ ...form, season: e.target.value })}>
                    <option value="">Any</option>
                    {['spring', 'summer', 'autumn', 'winter'].map((s) => <option key={s} value={s}>{titleCase(s)}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block font-label-md text-on-surface-variant mb-1">Size</label>
                  <input className="field" placeholder="e.g., M,L" value={form.size} onChange={(e) => setForm({ ...form, size: e.target.value })} />
                </div>
                <div>
                  <label className="block font-label-md text-on-surface-variant mb-1">Deadline</label>
                  <input type="date" className="field" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} />
                </div>
              </div>

              <div>
                <label className="block font-label-md text-on-surface-variant mb-2">Urgency *</label>
                <div className="flex items-center gap-3">
                  <input type="range" min="1" max="5" value={form.urgency} onChange={(e) => setForm({ ...form, urgency: e.target.value })} className="flex-1 accent-primary" />
                  <span className={`chip ${urgencyBadge(Number(form.urgency))} w-24 justify-center`}>
                    {['', 'Lower', '', '', '', 'Critical'][Number(form.urgency)] || form.urgency}/5
                  </span>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button type="button" className="btn-outline" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" disabled={saving} className="btn-primary">
                  {saving ? 'Publishing...' : 'Publish Need'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <Toast message={toast?.message} tone={toast?.tone} onClose={() => setToast(null)} />
    </div>
  );
}