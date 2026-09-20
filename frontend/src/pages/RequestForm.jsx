import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { MaterialIcon } from '../components/ui';
import Toast from '../components/Toast';

const CATEGORIES = [
  { value: 'clothes', label: 'Clothes', icon: 'checkroom' },
  { value: 'stationery', label: 'Educational Stationery', icon: 'menu_book' },
];

const SEASONS = ['', 'spring', 'summer', 'autumn', 'winter'];
const GENDERS = ['unisex', 'male', 'female'];

export default function RequestForm() {
  const [formData, setFormData] = useState({
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
  });
  const [error, setError] = useState('');
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const showToast = (message, tone = 'success') => {
    setToast({ message, tone });
    setTimeout(() => setToast(null), 3500);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = {
        ...formData,
        quantity_needed: parseInt(formData.quantity_needed, 10),
        urgency: parseInt(formData.urgency, 10),
        deadline: formData.deadline ? new Date(formData.deadline).toISOString() : undefined,
      };
      Object.keys(payload).forEach((key) => {
        if (payload[key] === '' || payload[key] === null || payload[key] === undefined) {
          delete payload[key];
        }
      });

      await api.post('/requests', payload);
      showToast('Request published');
      setTimeout(() => navigate('/ngo/dashboard'), 800);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface">
      <header className="sticky top-0 z-40 bg-surface-container-lowest/90 backdrop-blur-xl border-b border-surface-container-high">
        <div className="max-w-3xl mx-auto px-gutter-mobile h-16 flex items-center gap-3">
          <button type="button" onClick={() => navigate('/ngo/dashboard')} className="icon-btn" aria-label="Back">
            <MaterialIcon name="arrow_back" size={22} />
          </button>
          <h1 className="font-headline-md text-headline-md text-on-surface">Post a Request</h1>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-gutter-mobile py-6 pb-24">
        <form className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-6 flex flex-col gap-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-error-container text-on-error-container rounded-lg p-3.5 font-body-sm flex items-center gap-2">
              <MaterialIcon name="error" size={18} />{error}
            </div>
          )}

          <div className="flex flex-col gap-2">
            <span className="font-label-md text-on-surface">Category *</span>
            <div className="grid grid-cols-2 gap-3">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, category: cat.value })}
                  className={`flex items-center gap-2 rounded-full py-2.5 px-4 font-label-md transition-colors ${
                    formData.category === cat.value ? 'bg-tertiary-container text-on-tertiary-container' : 'bg-surface-container-low text-on-surface-variant'
                  }`}
                >
                  <MaterialIcon name={cat.icon} size={18} />
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="font-label-md text-on-surface">Item Type *</label>
              <input name="item_type" type="text" required placeholder="e.g., jackets, notebooks" value={formData.item_type} onChange={handleChange} className="field" />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label-md text-on-surface">Quantity Needed *</label>
              <input name="quantity_needed" type="number" min="1" required value={formData.quantity_needed} onChange={handleChange} className="field" />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label-md text-on-surface">Size</label>
              <input name="size" type="text" placeholder="e.g., M, L, 100 pages" value={formData.size} onChange={handleChange} className="field" />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label-md text-on-surface">Age Group</label>
              <input name="age_group" type="text" placeholder="e.g., 6-10, adult" value={formData.age_group} onChange={handleChange} className="field" />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label-md text-on-surface">Gender</label>
              <select name="gender" value={formData.gender} onChange={handleChange} className="field">
                {GENDERS.map((g) => <option key={g} value={g}>{g === 'unisex' ? 'Unisex' : g[0].toUpperCase() + g.slice(1)}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label-md text-on-surface">Season</label>
              <select name="season" value={formData.season} onChange={handleChange} className="field">
                <option value="">Any season</option>
                {SEASONS.filter(Boolean).map((s) => <option key={s} value={s}>{s[0].toUpperCase() + s.slice(1)}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label-md text-on-surface">Beneficiary Group</label>
              <input name="beneficiary_group" type="text" placeholder="e.g., underprivileged children" value={formData.beneficiary_group} onChange={handleChange} className="field" />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label-md text-on-surface">Deadline</label>
              <input name="deadline" type="date" value={formData.deadline} onChange={handleChange} className="field" />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <span className="font-label-md text-on-surface">Urgency *</span>
            <div className="flex items-center gap-3">
              <input type="range" min="1" max="5" value={formData.urgency} onChange={handleChange} name="urgency" className="flex-1 accent-primary" />
              <span className="chip bg-secondary-container text-on-secondary-container w-24 justify-center">
                {['', 'Low', 'Moderate', 'Elevated', 'High', 'Critical'][formData.urgency]} · {formData.urgency}/5
              </span>
            </div>
          </div>

          <div className="flex justify-end gap-3 border-t border-outline-variant/30 pt-5">
            <button type="button" className="btn-outline" onClick={() => navigate('/ngo/dashboard')}>Cancel</button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Creating...' : 'Create Request'}
            </button>
          </div>
        </form>
      </main>

      <Toast message={toast?.message} tone={toast?.tone} onClose={() => setToast(null)} />
    </div>
  );
}