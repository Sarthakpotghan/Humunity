import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { MaterialIcon, Avatar, StatusBadge } from '../components/ui';
import TopAppBar from '../components/layout/TopAppBar';
import Toast from '../components/Toast';
import { formatDateTime, formatDate, titleCase } from '../utils/format';

const statusFilters = ['all', 'scheduled', 'in_transit', 'delivered', 'confirmed'];

export default function VolunteerDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [deliveries, setDeliveries] = useState([]);
  const [error, setError] = useState('');
  const [toast, setToast] = useState(null);
  const [busy, setBusy] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');

  const loadDeliveries = useCallback(async () => {
    try {
      const res = await api.get('/deliveries');
      setDeliveries(res.data || []);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load deliveries');
    }
  }, []);

  useEffect(() => {
    loadDeliveries();
  }, [loadDeliveries]);

  const showToast = (message, tone = 'success') => {
    setToast({ message, tone });
    setTimeout(() => setToast(null), 3500);
  };

  const updateStatus = async (delivery, nextStatus) => {
    setBusy(`${delivery.id}-${nextStatus}`);
    try {
      await api.patch(`/deliveries/${delivery.id}/status`, { status: nextStatus });
      showToast(nextStatus === 'in_transit' ? 'Delivery started' : 'Marked as delivered');
      loadDeliveries();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Update failed', 'error');
    } finally {
      setBusy(null);
    }
  };

  const modeLabel = (mode) => (mode === 'pickup' ? 'Volunteer pickup' : 'Drop-off point');

  const stats = [
    { label: 'Assigned', value: deliveries.filter((d) => d.status === 'scheduled').length, icon: 'assignment_late', tone: 'secondary' },
    { label: 'In Transit', value: deliveries.filter((d) => d.status === 'in_transit').length, icon: 'local_shipping', tone: 'warning' },
    { label: 'Delivered', value: deliveries.filter((d) => d.status === 'delivered' || d.status === 'confirmed').length, icon: 'task_alt', tone: 'success' },
  ];

  const filtered = activeFilter === 'all'
    ? deliveries
    : deliveries.filter((d) => d.status === activeFilter);

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface antialiased">
      <TopAppBar subtitle="Volunteer Dashboard" />
      <main className="w-full max-w-6xl mx-auto px-margin-mobile pt-20 pb-24 space-y-6">
        <header className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-5 flex items-center gap-4">
          <Avatar name={user?.name} size={52} />
          <div className="min-w-0">
            <h1 className="font-headline-md text-headline-md text-on-surface truncate">{user?.name}</h1>
            <p className="font-body-sm text-on-surface-variant truncate">{user?.email} • Volunteer</p>
          </div>
        </header>

        {error && (
          <div className="bg-error-container text-on-error-container rounded-lg p-4 font-body-sm">
            {error}
          </div>
        )}

        <section className="grid grid-cols-3 gap-3">
          {stats.map((s) => (
            <div key={s.label} className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-4 flex flex-col gap-2">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                s.tone === 'success' ? 'bg-tertiary-container text-on-tertiary-container' : s.tone === 'warning' ? 'bg-secondary-fixed text-on-secondary-fixed-variant' : 'bg-secondary-container text-on-secondary-container'
              }`}>
                <MaterialIcon name={s.icon} size={22} />
              </div>
              <span className="font-display text-display-lg text-on-surface">{s.value}</span>
              <span className="font-label-sm text-on-surface-variant">{s.label}</span>
            </div>
          ))}
        </section>

        <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 overflow-hidden">
          <div className="px-5 pt-5 pb-3 flex items-center justify-between flex-wrap gap-2">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">My Deliveries</h2>
            <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
              {statusFilters.map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => setActiveFilter(f)}
                  className={`px-3 py-1.5 rounded-full font-label-md transition-colors shrink-0 ${
                    activeFilter === f ? 'bg-primary text-on-primary' : 'bg-surface-container-low text-on-surface-variant hover:text-on-surface'
                  }`}
                >
                  {f === 'all' ? 'All' : titleCase(f.replace('_', ' '))}
                </button>
              ))}
            </div>
          </div>

          {filtered.length === 0 ? (
            <div className="px-5 py-12 text-center">
              <MaterialIcon name="local_shipping" size={40} className="text-outline mx-auto mb-3" />
              <p className="font-body-md text-on-surface-variant">No {activeFilter !== 'all' ? activeFilter.replace('_', ' ') : ''} deliveries assigned to you</p>
              {deliveries.length === 0 && (
                <p className="font-body-sm text-on-surface-variant mt-1">The admin will assign you deliveries as they are scheduled.</p>
              )}
            </div>
          ) : (
            <div className="flex flex-col">
              {filtered.map((d) => (
                <article key={d.id} className="px-5 py-4 border-t border-outline-variant/20 flex flex-col gap-3">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-11 h-11 rounded-full bg-primary-container/50 text-on-primary-container flex items-center justify-center shrink-0">
                        <MaterialIcon name="inventory_2" size={22} />
                      </div>
                      <div className="min-w-0">
                        <p className="font-headline-sm text-headline-sm text-on-surface capitalize truncate">{d.donation_item}</p>
                        <p className="font-label-sm text-on-surface-variant">Qty {d.donation_quantity} • {modeLabel(d.mode)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <StatusBadge status={d.status} size="sm" />
                      {d.scheduled_at && (
                        <span className="chip bg-surface-container-high text-on-surface-variant">
                          <MaterialIcon name="schedule" size={15} /> {formatDateTime(d.scheduled_at)}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-body-sm text-on-surface-variant">
                    <div className="flex items-center gap-2">
                      <MaterialIcon name="inventory" size={16} />
                      <span className="truncate">Pickup: {d.donor_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MaterialIcon name="volunteer_activism" size={16} />
                      <span className="truncate">Deliver to: {d.ngo_name}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={() => navigate(`/map/${d.id}`)}
                      className="btn-outline px-4 py-2"
                    >
                      <MaterialIcon name="map" size={18} /> View route
                    </button>
                    {d.status === 'scheduled' && (
                      <button
                        type="button"
                        disabled={busy === `${d.id}-in_transit`}
                        onClick={() => updateStatus(d, 'in_transit')}
                        className="btn-primary px-4 py-2"
                      >
                        <MaterialIcon name="play_arrow" size={18} />
                        {busy === `${d.id}-in_transit` ? 'Starting...' : 'Start delivery'}
                      </button>
                    )}
                    {d.status === 'in_transit' && (
                      <button
                        type="button"
                        disabled={busy === `${d.id}-delivered`}
                        onClick={() => updateStatus(d, 'delivered')}
                        className="btn-primary px-4 py-2"
                      >
                        <MaterialIcon name="local_shipping" size={18} />
                        {busy === `${d.id}-delivered` ? 'Updating...' : 'Mark as delivered'}
                      </button>
                    )}
                    {d.status === 'delivered' && (
                      <span className="chip bg-tertiary-container text-on-tertiary-container">
                        <MaterialIcon name="hourglass_top" size={15} /> Awaiting NGO confirmation
                      </span>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>

      <Toast message={toast?.message} tone={toast?.tone} onClose={() => setToast(null)} />
    </div>
  );
}