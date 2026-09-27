import { useState } from 'react';
import { api } from '../services/api';
import { MaterialIcon } from './ui';

const starLabels = ['', 'Poor', 'Fair', 'Good', 'Very good', 'Excellent'];

export default function FeedbackForm({ matchId, onSubmitted, onClose }) {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [comments, setComments] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    if (!rating) {
      setError('Please select a rating');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await api.post('/feedback', {
        match_id: matchId,
        rating,
        comments: comments || undefined,
      });
      onSubmitted?.(rating);
      onClose?.();
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not submit feedback');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[90] bg-black/40 flex items-end md:items-center justify-center p-0 md:p-6" onClick={onClose}>
      <div
        className="bg-surface-container-lowest w-full md:max-w-md rounded-t-3xl md:rounded-lg max-h-[92dvh] overflow-y-auto no-scrollbar p-6 shadow-elevated animate-fade-up"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-headline-md text-headline-md text-on-surface">Rate this handover</h3>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close">
            <MaterialIcon name="close" size={22} />
          </button>
        </div>

        {error && (
          <div className="bg-error-container text-on-error-container rounded-lg p-3.5 font-body-sm mb-4">{error}</div>
        )}

        <form onSubmit={submit} className="space-y-5">
          <div className="flex flex-col items-center gap-2">
            <div className="flex gap-1.5">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHover(star)}
                  onMouseLeave={() => setHover(0)}
                  aria-label={`${star} star${star > 1 ? 's' : ''}`}
                  className="transition-transform hover:scale-110"
                >
                  <MaterialIcon
                    name={star <= (hover || rating) ? 'star' : 'star_border'}
                    size={34}
                    fill={star <= (hover || rating) ? 1 : 0}
                    className={star <= (hover || rating) ? 'text-amber-500' : 'text-outline'}
                  />
                </button>
              ))}
            </div>
            <span className="font-label-md text-on-surface-variant">{rating ? starLabels[rating] : 'Select a rating'}</span>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="font-label-md text-on-surface" htmlFor="fb-comments">Comments (optional)</label>
            <textarea
              id="fb-comments"
              rows={3}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="How was the handover experience?"
              className="field textarea"
            />
          </div>

          <div className="flex justify-end gap-3">
            <button type="button" className="btn-outline" onClick={onClose}>Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}