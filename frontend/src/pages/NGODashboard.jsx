import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { MaterialIcon, Avatar, StatusBadge } from '../components/ui';
import TopAppBar from '../components/layout/TopAppBar';
import Toast from '../components/Toast';
import RequestFormModal from '../components/RequestFormModal';
import {
  formatDate,
  formatDateTime,
  daysUntil,
  titleCase,
  categoryIcon,
  categoryLabel,
  urgencyBadge,
} from '../utils/format';



const statusFilters = ['all', 'active', 'fulfilled', 'closed'];

export default function NGODashboard() {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [matches, setMatches] = useState({});
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState('');
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');

  const loadAll = useCallback(async () => {
    try {
      const [reqRes, profileRes, matchesRes] = await Promise.all([
        api.get('/requests'),
        api.get('/auth/ngo/profile').catch(() => null),
        api.get('/requests/matches/all').catch(() => ({ data: [] })),
      ]);
      setRequests(reqRes.data || []);
      setProfile(profileRes?.data || null);
      
      const matchesByRequest = {};
      (matchesRes.data || []).forEach(match => {
        if (!matchesByRequest[match.request_id]) {
          matchesByRequest[match.request_id] = [];
        }
        matchesByRequest[match.request_id].push(match);
      });
      setMatches(matchesByRequest);
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

  ;

  const deadlineText = (req) => {
    const days = daysUntil(req.deadline);
    if (days === null) return null;
    if (days < 0) return { label: `Overdue by ${Math.abs(days)}d`, tone: 'error' };
    if (days === 0) return { label: 'Due today', tone: 'error' };
    return { label: `Due in ${days}d`, tone: days <= 2 ? 'error' : 'neutral' };
  };

  const handleAcceptMatch = async (matchId) => {
    setSaving(true);
    try {
      await api.patch(`/donations/matches/${matchId}/accept`);
      showToast('Match accepted successfully');
      loadAll();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to accept match', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleRejectMatch = async (matchId) => {
    setSaving(true);
    try {
      await api.patch(`/donations/matches/${matchId}/reject`);
      showToast('Match rejected');
      loadAll();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to reject match', 'error');
    } finally {
      setSaving(false);
    }
  };

  const MatchCard = ({ match, onAccept, onReject, saving }) => {
    const donation = match.donation;
    const donorArea = match.donor_area;
    const rank = match.score_breakdown?.rank;
    
    return (
      <div className="bg-surface-container-low rounded-lg p-3 border border-primary/20">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div className="flex-1 min-w-0 min-w-[200px]">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="font-label-md text-on-surface capitalize truncate">{donation?.item_type}</span>
              <span className="chip bg-primary-container text-on-primary-container font-label-sm">
                {(match.score * 100).toFixed(0)}% Match
              </span>
              {rank && (
                <span className={`chip font-label-sm ${rank === 1 ? 'bg-tertiary-container text-on-tertiary-container' : 'bg-surface-container-high text-on-surface-variant'}`}>
                  {rank === 1 ? (
                    <>
                      <MaterialIcon name="emoji_events" size={14} />
                      <span className="truncate ml-1">Rank #1 - Eligible to Accept</span>
                    </>
                  ) : (
                    <>
                      Rank #{rank} - Standby
                    </>
                  )}
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-2 text-body-sm text-on-surface-variant mb-2">
              <span className="flex items-center gap-1">
                <MaterialIcon name="inventory_2" size={14} /> Qty: {donation?.quantity}
              </span>
              <span className="flex items-center gap-1">
                <MaterialIcon name="star" size={14} /> Condition: {donation?.condition}
              </span>
              {donorArea && (
                <span className="flex items-center gap-1">
                  <MaterialIcon name="location_on" size={14} /> {donorArea}
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap shrink-0">
            {rank === 1 && (
              <button
                type="button"
                onClick={() => onAccept(match.id)}
                disabled={saving}
                className="btn-primary px-3 py-1.5"
              >
                <MaterialIcon name="check" size={16} /> Accept
              </button>
            )}
            {rank === 1 && (
              <button
                type="button"
                onClick={() => onReject(match.id)}
                disabled={saving}
                className="btn-outline px-3 py-1.5 text-error"
              >
                <MaterialIcon name="close" size={16} /> Reject
              </button>
            )}
            {rank && rank !== 1 && (
              <span className="btn-outline px-3 py-1.5 text-on-surface-variant" style={{cursor: 'not-allowed'}}>
                <MaterialIcon name="hourglass_empty" size={16} /> Standby
              </span>
            )}
          </div>
        </div>
      </div>
    );
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
                {user?.verified ? (
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
            <button type="button" onClick={() => setShowRequestForm(true)} className="btn-primary">
              <MaterialIcon name="add" size={20} />
              Post New Resource Need
            </button>
          </div>
        </header>

        {!user?.verified && (
          <div className="bg-surface-container-low rounded-lg p-4 flex items-center gap-3 border border-outline-variant/30">
            <MaterialIcon name="info" size={22} className="text-on-surface-variant" />
            <p className="font-body-sm text-on-surface-variant">
              Your NGO account is pending admin verification. You will be able to receive matches once approved.
            </p>
          </div>
        )}
        {user?.verified && !profile && (
          <div className="bg-surface-container-low rounded-lg p-4 flex items-center gap-3 border border-outline-variant/30">
            <MaterialIcon name="info" size={22} className="text-on-surface-variant" />
            <p className="font-body-sm text-on-surface-variant">
              Your NGO is verified! Complete your profile to receive matches and access all features.
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
              <button type="button" onClick={() => setShowRequestForm(true)} className="btn-tonal mt-4">
                <MaterialIcon name="add" size={18} /> Post your first need
              </button>
            </div>
          ) : (
            <div className="px-5 pb-5 grid grid-cols-1 md:grid-cols-2 gap-4">
              {activeNeeds.map((req) => {
                const dl = deadlineText(req);
                const requestMatches = matches[req.id] || [];
                const pendingMatches = requestMatches
                  .filter(m => m.status === 'pending')
                  .sort((a, b) => (a.score_breakdown?.rank || 999) - (b.score_breakdown?.rank || 999));
                const acceptedMatches = requestMatches.filter(m => m.status === 'accepted');
                const rejectedMatches = requestMatches.filter(m => m.status === 'rejected');
                
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
                    
                    {/* Incoming Matches Section */}
                    {pendingMatches.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-outline-variant/20">
                        <div className="flex items-center gap-2 mb-2">
                          <MaterialIcon name="sync_alt" size={18} className="text-primary" />
                          <span className="font-label-md text-on-surface">Incoming Matches ({pendingMatches.length})</span>
                        </div>
                        <div className="space-y-2">
                          {pendingMatches.map((match) => (
                            <MatchCard key={match.id} match={match} onAccept={() => handleAcceptMatch(match.id)} onReject={() => handleRejectMatch(match.id)} saving={saving} />
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {acceptedMatches.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-outline-variant/20">
                        <div className="flex items-center gap-2 mb-2">
                          <MaterialIcon name="check_circle" size={18} className="text-tertiary" />
                          <span className="font-label-md text-on-surface">Accepted ({acceptedMatches.length})</span>
                        </div>
                        <div className="space-y-2">
                          {acceptedMatches.map((match) => (
                            <div key={match.id} className="bg-tertiary-container/30 rounded-lg p-3">
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-label-md text-on-surface capitalize">{match.donation?.item_type}</p>
                                  <p className="font-label-sm text-on-surface-variant">Qty: {match.donation?.quantity} • Score: {(match.score * 100).toFixed(0)}%</p>
                                </div>
                                <span className="chip bg-tertiary-container text-on-tertiary-container">
                                  <MaterialIcon name="check" size={14} /> Accepted
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {rejectedMatches.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-outline-variant/20">
                        <div className="flex items-center gap-2 mb-2">
                          <MaterialIcon name="cancel" size={18} className="text-error" />
                          <span className="font-label-md text-on-surface">Rejected ({rejectedMatches.length})</span>
                        </div>
                        <div className="space-y-2">
                          {rejectedMatches.map((match) => (
                            <div key={match.id} className="bg-error-container/30 rounded-lg p-3">
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-label-md text-on-surface capitalize">{match.donation?.item_type}</p>
                                  <p className="font-label-sm text-on-surface-variant">Qty: {match.donation?.quantity} • Score: {(match.score * 100).toFixed(0)}%</p>
                                </div>
                                <span className="chip bg-error-container text-on-error-container">
                                  <MaterialIcon name="close" size={14} /> Rejected
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {requestMatches.length === 0 && (
                      <div className="mt-3 pt-3 border-t border-outline-variant/20 text-center text-body-sm text-on-surface-variant">
                        <MaterialIcon name="sync_problem" size={20} className="mx-auto mb-1 text-outline" />
                        <p>No incoming matches yet. Matches appear here when donors run matching.</p>
                      </div>
                    )}
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

{showRequestForm && (
          <RequestFormModal isOpen={showRequestForm} onClose={() => setShowRequestForm(false)} />
        )}

      <Toast message={toast?.message} tone={toast?.tone} onClose={() => setToast(null)} />
    </div>
  );
}