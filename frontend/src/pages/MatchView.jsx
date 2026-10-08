import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { MaterialIcon, StatusBadge } from '../components/ui';
import Toast from '../components/Toast';
import { useDonorData } from '../hooks/useDonorData';
import { formatDate, formatScore, titleCase, categoryIcon, categoryLabel } from '../utils/format';

const breakdownLabels = {
  urgency: 'Urgency',
  similarity: 'Similarity',
  seasonal: 'Seasonal',
  proximity: 'Proximity',
  quantity_fit: 'Quantity Fit',
  condition: 'Condition',
  reliability: 'Reliability',
};

export default function MatchView() {
  const { donationId } = useParams();
  const { donations } = useDonorData();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matching, setMatching] = useState(false);
  const [toast, setToast] = useState(null);
  const navigate = useNavigate();

  const donation = donations.find((d) => String(d.id) === donationId);

  const fetchMatches = useCallback(async () => {
    try {
      const response = await api.get(`/donations/${donationId}/matches`);
      setMatches(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load matches');
    } finally {
      setLoading(false);
    }
  }, [donationId]);

  useEffect(() => {
    setLoading(true);
    setError('');
    fetchMatches();
  }, [fetchMatches]);

  const handleRunMatching = async () => {
    setMatching(true);
    setError('');
    try {
      await api.post(`/donations/${donationId}/match`);
      setToast({ message: 'Matching engine ran successfully', tone: 'success' });
      setTimeout(() => setToast(null), 3500);
      fetchMatches();
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not run matching');
    } finally {
      setMatching(false);
    }
  };

  if (loading && matches.length === 0) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface">
      <header className="sticky top-0 z-40 bg-surface-container-lowest/90 backdrop-blur-xl border-b border-surface-container-high">
        <div className="max-w-4xl mx-auto px-gutter-mobile h-16 flex items-center gap-3">
          <button type="button" onClick={() => navigate('/donor/dashboard/items')} className="icon-btn" aria-label="Back">
            <MaterialIcon name="arrow_back" size={22} />
          </button>
          <h1 className="font-headline-md text-headline-md text-on-surface">Matched NGOs</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-gutter-mobile py-6 pb-16 flex flex-col gap-5">
        {error && (
          <div className="bg-error-container text-on-error-container rounded-lg p-4 font-body-sm flex items-center gap-2">
            <MaterialIcon name="error" size={18} />
            <span className="flex-1">{error}</span>
            <button type="button" onClick={() => setError('')} aria-label="Dismiss"><MaterialIcon name="close" size={18} /></button>
          </div>
        )}

        {donation && (
          <div className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-primary-container/50 text-on-primary-container flex items-center justify-center shrink-0">
              <MaterialIcon name={categoryIcon(donation.category)} size={24} />
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-headline-sm text-headline-sm text-on-surface truncate capitalize">{donation.item_type}</p>
              <p className="font-body-sm text-on-surface-variant">
                {categoryLabel(donation.category)} · Qty {donation.quantity} · Listed {formatDate(donation.created_at)}
              </p>
            </div>
            <StatusBadge status={donation.status} size="md" />
          </div>
        )}

        {donation?.status === 'listed' && (
          <button type="button" onClick={handleRunMatching} disabled={matching} className="btn-primary self-start">
            <MaterialIcon name="sync_alt" size={20} />
            {matching ? 'Running matching...' : matches.length === 0 ? 'Run Matching' : 'Run Matching Again'}
          </button>
        )}

        {matches.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl p-10 text-center border border-outline-variant/20">
            <MaterialIcon name="volunteer_activism" size={48} className="text-outline mx-auto mb-3" />
            <h3 className="font-headline-sm text-headline-sm text-on-surface mb-1">No matches found yet</h3>
            <p className="font-body-sm text-on-surface-variant">
              {donation?.status === 'listed'
                ? 'Run the matching engine to find NGOs that need these items.'
                : 'This donation has no active matches right now.'}
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {matches.map((match) => {
              const breakdown = match.score_breakdown || {};
              return (
                <div key={match.id} className="bg-surface-container-lowest rounded-2xl p-6 shadow-card border border-outline-variant/20">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 flex-wrap">
                          {match.ngo_name ? (
                            <span className="font-headline-sm text-headline-sm text-on-surface">{match.ngo_name}</span>
                          ) : (
                            <span className="font-headline-sm text-headline-sm text-on-surface">Request #{match.request_id}</span>
                          )}
                          <StatusBadge status={match.status} size="sm" />
                        </div>
                      <div className="flex items-center gap-2 mt-2">
                        <div className="h-2 w-32 rounded-full bg-surface-container-high overflow-hidden">
                          <div className="h-full rounded-full bg-tertiary" style={{ width: `${Math.min(100, (match.score || 0) * 100)}%` }} />
                        </div>
                        <span className="font-label-lg text-on-surface">{formatScore(match.score)}</span>
                        <span className="font-label-sm text-on-surface-variant">match score</span>
                      </div>
                      <p className="font-label-sm text-on-surface-variant mt-1">Matched {formatDate(match.created_at)}</p>
                    </div>
                  </div>

                  {Object.keys(breakdown).length > 0 && (
                    <div className="mt-5">
                      <p className="font-label-md text-on-surface-variant mb-2">Score Breakdown</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {Object.entries(breakdown).map(([key, data]) => (
                          <div key={key} className="bg-surface-container-low rounded-lg p-2.5">
                            <div className="flex items-center justify-between gap-2">
                              <span className="font-label-sm text-on-surface-variant truncate">{breakdownLabels[key] || titleCase(key)}</span>
                              <span className="font-label-sm font-bold text-on-surface">{formatScore(data?.value)}</span>
                            </div>
                            <div className="mt-1.5 h-1 rounded-full bg-surface-container-highest overflow-hidden">
                              <div className="h-full rounded-full bg-primary" style={{ width: `${Math.min(100, (data?.value || 0) * 100)}%` }} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {breakdown.rank && (
                    <div className="mt-4 flex items-center gap-2">
                      {breakdown.rank === 1 ? (
                        <>
                          <MaterialIcon name="emoji_events" size={18} className="text-tertiary" />
                          <span className="font-label-md text-on-surface text-tertiary font-bold">Rank #1 — Eligible to Accept</span>
                        </>
                      ) : (
                        <>
                          <MaterialIcon name="hourglass_empty" size={18} className="text-on-surface-variant" />
                          <span className="font-label-md text-on-surface-variant">Rank #{breakdown.rank} — Standby</span>
                        </>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        <button type="button" onClick={() => navigate('/donor/dashboard/matches')} className="btn-outline self-start">
          <MaterialIcon name="list" size={18} /> All matches
        </button>
      </main>

      <Toast message={toast?.message} tone={toast?.tone} onClose={() => setToast(null)} />
    </div>
  );
}