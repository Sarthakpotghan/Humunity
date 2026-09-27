import { useCallback, useEffect, useMemo, useState } from 'react';
import { MaterialIcon, StatusBadge } from '../../components/ui';
import { useDonorData } from '../../hooks/useDonorData';
import { api } from '../../services/api';
import FeedbackForm from '../../components/FeedbackForm';
import Toast from '../../components/Toast';
import { formatDate, formatScore, titleCase } from '../../utils/format';

const breakdownLabels = {
  urgency: 'Urgency',
  similarity: 'Similarity',
  seasonal: 'Seasonal',
  proximity: 'Proximity',
  quantity_fit: 'Quantity Fit',
  condition: 'Condition',
  reliability: 'Reliability',
  priority_match: 'Priority',
};

const COMPLETED = ['delivered', 'confirmed'];

export default function MyMatches() {
  const { donations, matches, deliveries, loading, error } = useDonorData();
  const [feedbackGiven, setFeedbackGiven] = useState({});
  const [feedbackFor, setFeedbackFor] = useState(null);
  const [toast, setToast] = useState(null);

  const completedDeliveryMatchIds = useMemo(
    () => new Set(deliveries.filter((d) => COMPLETED.includes(d.status)).map((d) => d.match_id)),
    [deliveries]
  );

  const showToast = (message, tone = 'success') => {
    setToast({ message, tone });
    setTimeout(() => setToast(null), 3500);
  };

  const loadFeedback = useCallback(async () => {
    const ids = matches
      .filter((m) => completedDeliveryMatchIds.has(m.id))
      .map((m) => m.id);
    const given = {};
    await Promise.all(ids.map(async (id) => {
      try {
        const res = await api.get(`/feedback/match/${id}`);
        if (res.data?.length) given[id] = true;
      } catch (e) {
        // ignore
      }
    }));
    setFeedbackGiven(given);
  }, [matches, completedDeliveryMatchIds]);

  useEffect(() => {
    if (matches.length) loadFeedback();
  }, [matches, loadFeedback]);

  const pending = matches.filter((m) => m.status === 'pending');
  const sorted = [...matches].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h1 className="font-headline-md text-headline-md text-on-surface">My Matches</h1>
        <span className="chip self-start sm:self-auto bg-primary-container/60 text-on-primary-container">
          {pending.length} pending
        </span>
      </div>

      {error && (
        <div className="bg-error-container text-on-error-container rounded-lg p-4 font-body-sm">{error}</div>
      )}

      {loading && matches.length === 0 ? (
        <div className="flex items-center justify-center h-48 text-on-surface-variant">Loading...</div>
      ) : sorted.length === 0 ? (
        <div className="bg-surface-container-lowest rounded-2xl p-10 text-center border border-outline-variant/20">
          <MaterialIcon name="sync_alt" size={48} className="text-outline mx-auto mb-3" />
          <h3 className="font-headline-sm text-headline-sm text-on-surface mb-1">No matches yet</h3>
          <p className="font-body-sm text-on-surface-variant">
            {donations.some((d) => d.status === 'listed')
              ? 'Run the matching engine from one of your listed items.'
              : 'List a donation and run matching to find NGO partners.'}
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {sorted.map((match) => {
            const donation = donations.find((x) => x.id === match.donation_id);
            const breakdown = match.score_breakdown || {};
            return (
              <div key={match.id} className="bg-surface-container-lowest rounded-2xl p-6 shadow-card border border-outline-variant/20">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className="w-12 h-12 rounded-full bg-primary-container/50 text-on-primary-container flex items-center justify-center shrink-0">
                      <MaterialIcon name="volunteer_activism" size={22} />
                    </div>
                    <div className="min-w-0">
                      <p className="font-label-lg text-on-surface truncate">
                        {donation ? titleCase(donation.item_type) : `Donation #${match.donation_id}`}
                      </p>
                      <p className="font-label-sm text-on-surface-variant">
                        Match #R{match.request_id} · {formatDate(match.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <div className="h-2 w-24 rounded-full bg-surface-container-high overflow-hidden">
                          <div className="h-full rounded-full bg-tertiary" style={{ width: `${Math.min(100, (match.score || 0) * 100)}%` }} />
                        </div>
                        <span className="font-headline-sm text-on-surface">{formatScore(match.score)}</span>
                      </div>
                      <span className="font-label-sm text-on-surface-variant">match score</span>
                    </div>
                    <StatusBadge status={match.status} size="md" />
                  </div>
                </div>

                {completedDeliveryMatchIds.has(match.id) && (
                  <div className="mt-4 pt-4 border-t border-outline-variant/20">
                    {feedbackGiven[match.id] ? (
                      <span className="inline-flex items-center gap-1.5 chip bg-tertiary-container text-on-tertiary-container">
                        <MaterialIcon name="check_circle" size={16} /> Thanks for rating this handover
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setFeedbackFor(match.id)}
                        className="btn-tonal px-4 py-2"
                      >
                        <MaterialIcon name="star" size={18} /> Rate this handover
                      </button>
                    )}
                  </div>
                )}

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
              </div>
            );
          })}
        </div>
      )}

      {feedbackFor && (
        <FeedbackForm
          matchId={feedbackFor}
          onSubmitted={(rating) => {
            setFeedbackGiven((prev) => ({ ...prev, [feedbackFor]: true }));
            showToast(`Thanks for rating ${rating} star${rating > 1 ? 's' : ''}!`);
          }}
          onClose={() => setFeedbackFor(null)}
        />
      )}

      <Toast message={toast?.message} tone={toast?.tone} onClose={() => setToast(null)} />
    </div>
  );
}