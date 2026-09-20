import { useMemo, useState } from 'react';
import { MaterialIcon, StatusBadge } from '../../components/ui';
import { NavLink, useNavigate } from 'react-router-dom';
import { useDonorData } from '../../hooks/useDonorData';
import Toast from '../../components/Toast';
import { api } from '../../services/api';
import { formatDate, titleCase, categoryIcon, categoryLabel } from '../../utils/format';

const filters = ['all', 'listed', 'matched', 'accepted', 'in_transit', 'delivered'];

export default function MyItems() {
  const { donations, loading, error, refetch } = useDonorData();
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [busy, setBusy] = useState(null);
  const [toast, setToast] = useState(null);
  const navigate = useNavigate();

  const filtered = useMemo(() => {
    return donations.filter((d) => {
      const matchesFilter = filter === 'all' || d.status === filter;
      const q = search.trim().toLowerCase();
      const matchesSearch = !q ||
        d.item_type.toLowerCase().includes(q) ||
        d.category.toLowerCase().includes(q) ||
        String(d.id).includes(q);
      return matchesFilter && matchesSearch;
    });
  }, [donations, filter, search]);

  const showToast = (message, tone = 'success') => {
    setToast({ message, tone });
    setTimeout(() => setToast(null), 3500);
  };

  const handleDelete = async (id) => {
    setBusy(id);
    try {
      await api.delete(`/donations/${id}`);
      showToast('Donation removed');
      setConfirmDelete(null);
      refetch();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Could not delete donation', 'error');
    } finally {
      setBusy(null);
    }
  };

  const handleRunMatching = async (id) => {
    setBusy(id);
    try {
      await api.post(`/donations/${id}/match`);
      showToast('Matching engine ran — check your matches');
      refetch();
      navigate(`/matches/${id}`);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Could not run matching', 'error');
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h1 className="font-headline-md text-headline-md text-on-surface">My Items</h1>
        <NavLink to="/donation/new" className="btn-primary self-start sm:self-auto">
          <MaterialIcon name="add" size={20} />
          <span>List New Item</span>
        </NavLink>
      </div>

      <div className="flex flex-wrap gap-2">
        {filters.map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-full font-label-md transition-colors ${
              filter === f
                ? 'bg-primary text-on-primary shadow-sm'
                : 'bg-surface-container-lowest text-on-surface-variant hover:text-on-surface border border-outline-variant/30'
            }`}
          >
            {titleCase(f)}
          </button>
        ))}
      </div>

      <div className="relative">
        <MaterialIcon name="search" size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant" />
        <input
          type="text"
          placeholder="Search items..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="field pl-11"
        />
      </div>

      {error && (
        <div className="bg-error-container text-on-error-container rounded-lg p-4 font-body-sm">{error}</div>
      )}

      {loading && donations.length === 0 ? (
        <div className="flex items-center justify-center h-48 text-on-surface-variant">Loading...</div>
      ) : (
        <div className="flex flex-col gap-3">
          {filtered.length === 0 ? (
            <div className="bg-surface-container-lowest rounded-2xl p-10 text-center border border-outline-variant/20">
              <MaterialIcon name="inventory_2" size={48} className="text-outline mx-auto mb-3" />
              <h3 className="font-headline-sm text-headline-sm text-on-surface mb-1">No items found</h3>
              <p className="font-body-sm text-on-surface-variant">Try adjusting your filters or list a new donation</p>
            </div>
          ) : (
            filtered.map((donation) => (
              <div key={donation.id} className="bg-surface-container-lowest rounded-2xl p-4 shadow-card border border-outline-variant/20">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className="w-12 h-12 rounded-full bg-primary-container/50 text-on-primary-container flex items-center justify-center shrink-0">
                      <MaterialIcon name={categoryIcon(donation.category)} size={24} />
                    </div>
                    <div className="flex flex-col min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-label-lg text-on-surface font-bold truncate capitalize">{donation.item_type}</span>
                        <span className="px-2 py-0.5 bg-surface-container-low text-on-surface-variant rounded-md font-label-sm text-[10px]">{categoryLabel(donation.category)}</span>
                      </div>
                      <div className="flex items-center gap-2 text-body-sm text-on-surface-variant mt-1 flex-wrap">
                        <span>Qty <span className="font-bold">{donation.quantity}</span></span>
                        {donation.size && <span>· Size {donation.size}</span>}
                        {donation.age_group && <span>· {donation.age_group}</span>}
                        {donation.gender && <span>· {titleCase(donation.gender)}</span>}
                        {donation.season && <span>· {titleCase(donation.season)}</span>}
                      </div>
                      <div className="flex items-center gap-2 text-body-sm text-on-surface-variant mt-1">
                        <span className="capitalize">Condition: {donation.condition}</span>
                        <span>· Listed {formatDate(donation.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2 shrink-0">
                    <StatusBadge status={donation.status} size="md" />
                    <div className="flex items-center gap-1.5">
                      {donation.status === 'listed' && (
                        <>
                          <button
                            type="button"
                            disabled={busy === donation.id}
                            onClick={() => handleRunMatching(donation.id)}
                            className="btn-tonal px-3 py-1.5"
                          >
                            <MaterialIcon name="sync_alt" size={16} />
                            <span className="hidden sm:inline">Run Matching</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => setConfirmDelete(donation.id)}
                            className="btn-outline px-3 py-1.5 text-error"
                            aria-label="Delete donation"
                          >
                            <MaterialIcon name="delete" size={16} />
                          </button>
                        </>
                      )}
                      <NavLink to={`/matches/${donation.id}`} className="btn-outline px-3 py-1.5">
                        <MaterialIcon name="find_in_page" size={16} />
                        <span className="hidden sm:inline">Matches</span>
                      </NavLink>
                    </div>
                  </div>
                </div>

                {confirmDelete === donation.id && (
                  <div className="mt-4 rounded-lg bg-error-container text-on-error-container p-4 flex flex-col sm:flex-row sm:items-center gap-3">
                    <p className="font-body-sm flex-1">Delete this donation? This cannot be undone.</p>
                    <div className="flex gap-2">
                      <button type="button" className="btn-ghost px-3 py-1.5 text-on-error-container" onClick={() => setConfirmDelete(null)}>Cancel</button>
                      <button
                        type="button"
                        disabled={busy === donation.id}
                        onClick={() => handleDelete(donation.id)}
                        className="px-4 py-1.5 rounded-full bg-error text-on-error font-label-md"
                      >
                        {busy === donation.id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      <Toast message={toast?.message} tone={toast?.tone} onClose={() => setToast(null)} />
    </div>
  );
}