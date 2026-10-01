import { useState, useRef, useNavigate } from 'react';
import { api } from '../services/api';
import { MaterialIcon } from '../components/ui';
import Toast from '../components/Toast';
import { formatDate, titleCase, categoryIcon, categoryLabel } from '../utils/format';

const CONDITIONS = [
  { value: 'new', label: 'New' },
  { value: 'good', label: 'Good' },
  { value: 'fair', label: 'Fair' },
];

const CATEGORIES = [
  { value: 'clothes', label: 'Clothes', icon: 'checkroom' },
  { value: 'stationery', label: 'Educational Stationery', icon: 'menu_book' },
];

const SEASONS = ['', 'spring', 'summer', 'autumn', 'winter'];
const GENDERS = ['unisex', 'male', 'female'];

export default function CreateDonationModal({ isOpen, onClose }) {
  const [formData, setFormData] = useState({
    category: 'clothes',
    item_type: '',
    size: '',
    age_group: '',
    gender: 'unisex',
    season: '',
    condition: 'good',
    quantity: 1,
    description: '',
    lat: '',
    lng: '',
    available_from: '',
    available_to: '',
  });
  const [photos, setPhotos] = useState([]);
  const [photoPreviews, setPhotoPreviews] = useState([]);
  const fileInputRef = useRef(null);
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

  const handlePhotoSelect = (e) => {
    const files = Array.from(e.target.files);
    const newPreviews = files.map(file => URL.createObjectURL(file));
    setPhotoPreviews(prev => [...prev, ...newPreviews]);
    setPhotos(prev => [...prev, ...files]);
  };

  const removePhoto = (index) => {
    setPhotoPreviews(prev => prev.filter((_, i) => i !== index));
    setPhotos(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = {
        ...formData,
        quantity: parseInt(formData.quantity, 10),
        lat: formData.lat === '' ? undefined : parseFloat(formData.lat),
        lng: formData.lng === '' ? undefined : parseFloat(formData.lng),
        available_from: formData.available_from ? new Date(formData.available_from).toISOString() : undefined,
        available_to: formData.available_to ? new Date(formData.available_to).toISOString() : undefined,
      };
      Object.keys(payload).forEach((key) => {
        if (payload[key] === '' || payload[key] === null || payload[key] === undefined) {
          delete payload[key];
        }
      });

      const response = await api.post('/donations', payload);
      const donationId = response.data.id;

      for (const file of photos) {
        const photoForm = new FormData();
        photoForm.append('file', file);
        await api.post(`/donations/${donationId}/photos`, photoForm, {
          headers: { 'Content-Type': 'multipart/form-data' },
        }).catch(() => {});
      }

      showToast('Donation listed! Running matching engine...');
      setTimeout(() => navigate(`/matches/${donationId}`), 800);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create donation');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[90] bg-black/40 flex items-end md:items-center justify-center p-0 md:p-6" onClick={onClose}>
      <div
        className="bg-surface-container-lowest w-full md:max-w-2xl rounded-t-3xl md:rounded-lg max-h-[92dvh] overflow-y-auto no-scrollbar p-6 shadow-elevated animate-fade-up"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-headline-md text-headline-md text-on-surface">List a Donation</h3>
          <button type="button" onClick={onClose} className="icon-btn" aria-label="Close">
            <MaterialIcon name="close" size={22} />
          </button>
        </div>

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
                <label className="font-label-md text-on-surface">Condition *</label>
                <select name="condition" value={formData.condition} onChange={handleChange} required className="field">
                  {CONDITIONS.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="font-label-md text-on-surface">Quantity *</label>
                <input name="quantity" type="number" min="1" required value={formData.quantity} onChange={handleChange} className="field" />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="font-label-md text-on-surface">Size</label>
                <input name="size" type="text" placeholder="e.g., M, L, 100 pages" value={formData.size} onChange={handleChange} className="field" />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="block font-label-md text-on-surface">Age Group</label>
                <input name="age_group" type="text" placeholder="e.g., 6-10, adult" value={formData.age_group} onChange={handleChange} className="field" />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="block font-label-md text-on-surface">Gender</label>
                <select name="gender" value={formData.gender} onChange={handleChange} className="field">
                  {GENDERS.map((g) => <option key={g} value={g}>{g === 'unisex' ? 'Unisex' : g[0].toUpperCase() + g.slice(1)}</option>)}
                </select>
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="block font-label-md text-on-surface">Season</label>
                <select name="season" value={formData.season} onChange={handleChange} className="field">
                  <option value="">Any season</option>
                  {SEASONS.filter(Boolean).map((s) => <option key={s} value={s}>{s[0].toUpperCase() + s.slice(1)}</option>)}
                </select>
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="block font-label-md text-on-surface">Size</label>
                <input name="size" type="text" placeholder="e.g., M, L, 100 pages" value={formData.size} onChange={handleChange} className="field" />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="block font-label-md text-on-surface">Deadline</label>
                <input name="available_to" type="date" className="field" value={formData.available_to} onChange={handleChange} />
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <span className="font-label-md text-on-surface">Description</label>
              <textarea rows={3} name="description" placeholder="Describe the items, e.g. '10 warm jackets for kids 6-10'. Matching details are extracted automatically." value={formData.description} onChange={handleChange} className="field textarea" />
            </div>

            <div className="flex flex-col gap-2">
              <span className="font-label-md text-on-surface">Photos</span>
              <p className="font-body-sm text-on-surface-variant">Add up to 5 photos of the items. Helps NGOs assess condition.</p>
              <div className="flex flex-wrap gap-3">
                {photoPreviews.map((preview, index) => (
                  <div key={index} className="relative w-24 h-24 rounded-lg overflow-hidden border border-outline-variant/40 group">
                    <img src={preview} alt={`Preview ${index + 1}`} className="w-full h-full object-cover" />
                    <button
                      type="button"
                      onClick={() => removePhoto(index)}
                      className="absolute top-1 right-1 w-6 h-6 rounded-full bg-error text-on-error flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      aria-label="Remove photo"
                    >
                      <MaterialIcon name="close" size={14} />
                    </button>
                  </div>
                ))}
                {photos.length < 5 && (
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="w-24 h-24 rounded-lg border-2 border-dashed border-outline-variant/60 flex flex-col items-center justify-center gap-1 text-on-surface-variant hover:border-primary hover:text-primary transition-colors"
                  >
                    <MaterialIcon name="add_a_photo" size={24} />
                    <span className="font-label-sm">Add</span>
                  </button>
                )}
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                onChange={handlePhotoSelect}
                className="hidden"
              />
            </div>

            <div className="flex flex-col gap-3 border-t border-outline-variant/30 pt-5">
              <span className="font-headline-sm text-headline-sm text-on-surface">Location & Availability</span>
              <p className="font-body-sm text-on-surface-variant">
                Leave coordinates blank to use your profile location. Optional latitude/longitude numbers help volunteers find you.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="font-label-md text-on-surface">Latitude</label>
                  <input name="lat" type="number" step="any" placeholder="e.g., 28.6139" value={formData.lat} onChange={handleChange} className="field" />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="font-label-md text-on-surface">Longitude</label>
                  <input name="lng" type="number" step="any" placeholder="e.g., 77.2090" value={formData.lng} onChange={handleChange} className="field" />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="font-label-md text-on-surface">Available From</label>
                  <input name="available_from" type="datetime-local" value={formData.available_from} onChange={handleChange} className="field" />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="font-label-md text-on-surface">Available Until</label>
                  <input name="available_to" type="datetime-local" value={formData.available_to} onChange={handleChange} className="field" />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 border-t border-outline-variant/30 pt-5">
              <button type="button" className="btn-outline" onClick={onClose}>Cancel</button>
              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? 'Listing...' : 'List Donation'}
              </button>
            </div>
          </form>
        </main>

        <Toast message={toast?.message} tone={toast?.tone} onClose={() => setToast(null)} />
      </div>
    </div>
  );
}

const CONDITIONS = [
  { value: 'new', label: 'New' },
  { value: 'good', label: 'Good' },
  { value: 'fair', label: 'Fair' },
];

const CATEGORIES = [
  { value: 'clothes', label: 'Clothes', icon: 'checkroom' },
  { value: 'stationery', label: 'Educational Stationery', icon: 'menu_book' },
];

const SEASONS = ['', 'spring', 'summer', 'autumn', 'winter'];
const GENDERS = ['unisex', 'male', 'female'];

export default CreateDonationModal;