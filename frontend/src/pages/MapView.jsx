import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { api } from '../services/api';
import { MaterialIcon, StatusBadge } from '../components/ui';
import { formatDateTime, titleCase } from '../utils/format';

const defaultPosition = [28.6139, 77.2090];

const iconColors = { start: '#2c694e', end: '#79545c' };

const startIcon = L.divIcon({
  className: 'bg-transparent',
  html: `<div style="width:32px;height:32px;border-radius:50%;background:${iconColors.start};color:#fff;display:flex;align-items:center;justify-content:center;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.25);font-size:14px;">P</div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
});

const endIcon = L.divIcon({
  className: 'bg-transparent',
  html: `<div style="width:32px;height:32px;border-radius:50%;background:${iconColors.end};color:#fff;display:flex;align-items:center;justify-content:center;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.25);font-size:14px;">D</div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
});

export default function MapView() {
  const { deliveryId } = useParams();
  const [delivery, setDelivery] = useState(null);
  const [events, setEvents] = useState([]);
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const fetchDelivery = useCallback(async () => {
    try {
      const [deliveryRes, routeRes, eventsRes] = await Promise.all([
        api.get(`/deliveries/${deliveryId}`),
        api.get(`/deliveries/${deliveryId}/route`),
        api.get(`/deliveries/${deliveryId}/events`).catch(() => ({ data: [] })),
      ]);
      setDelivery(deliveryRes.data);
      setRoute(routeRes.data);
      setEvents(eventsRes.data || []);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load delivery');
    } finally {
      setLoading(false);
    }
  }, [deliveryId]);

  useEffect(() => {
    setLoading(true);
    fetchDelivery();
  }, [fetchDelivery]);

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const coords = route?.geometry?.coordinates?.map(([lng, lat]) => [lat, lng]) || [];
  const start = coords[0] || defaultPosition;
  const end = coords[coords.length - 1] || defaultPosition;
  const center = start;

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface flex flex-col">
      <header className="sticky top-0 z-40 bg-surface-container-lowest/90 backdrop-blur-xl border-b border-surface-container-high">
        <div className="max-w-4xl mx-auto px-gutter-mobile h-16 flex items-center gap-3">
          <button type="button" onClick={() => navigate(-1)} className="icon-btn" aria-label="Back">
            <MaterialIcon name="arrow_back" size={22} />
          </button>
          <h1 className="font-headline-md text-headline-md text-on-surface">Delivery Tracking</h1>
          {delivery && <StatusBadge status={delivery.status} size="sm" className="ml-auto" />}
        </div>
      </header>

      <main className="max-w-4xl w-full mx-auto flex-1 flex flex-col">
        {error && (
          <div className="m-4 bg-error-container text-on-error-container rounded-lg p-4 font-body-sm flex items-center gap-2">
            <MaterialIcon name="error" size={18} />{error}
          </div>
        )}

        {delivery && (
          <div className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 m-4 mb-0 p-4 grid grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <span className="block font-label-sm text-on-surface-variant">Mode</span>
              <span className="font-label-md text-on-surface capitalize">{titleCase(delivery.mode)}</span>
            </div>
            <div>
              <span className="block font-label-sm text-on-surface-variant">Status</span>
              <span className="font-label-md text-on-surface capitalize">{titleCase(delivery.status)}</span>
            </div>
            <div>
              <span className="block font-label-sm text-on-surface-variant">Scheduled</span>
              <span className="font-label-md text-on-surface">{delivery.scheduled_at ? formatDateTime(delivery.scheduled_at) : 'Not scheduled'}</span>
            </div>
            <div>
              <span className="block font-label-sm text-on-surface-variant">Trip</span>
              <span className="font-label-md text-on-surface">
                {route?.distance ? `${route.distance.toFixed(1)} km · ${Math.round(route.duration)} min` : 'Route unavailable'}
              </span>
            </div>
          </div>
        )}

        <div className="flex-1 min-h-[380px] m-4 rounded-lg overflow-hidden shadow-card border border-outline-variant/30">
          <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {coords.length > 0 && (
              <Polyline positions={coords} color="#79545c" weight={4} opacity={0.85} />
            )}
            <Marker position={start} icon={startIcon}>
              <Popup><strong>Pickup point</strong><br />Start of route</Popup>
            </Marker>
            <Marker position={end} icon={endIcon}>
              <Popup><strong>Drop-off point</strong><br />End of route</Popup>
            </Marker>
          </MapContainer>
        </div>

        {events.length > 0 && (
          <div className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 m-4 mt-0 p-5">
            <h3 className="font-headline-sm text-headline-sm text-on-surface mb-4">Timeline</h3>
            <div className="space-y-3">
              {[...events].reverse().map((event, i) => (
                <div key={event.id} className="flex items-start gap-3">
                  <div className="flex flex-col items-center self-stretch">
                    <span className={`w-3 h-3 rounded-full mt-1.5 ${i === 0 ? 'bg-primary' : 'bg-outline-variant'}`} />
                    {i < events.length - 1 && <span className="w-0.5 flex-1 bg-outline-variant mt-1" />}
                  </div>
                  <div className="flex-1 pb-1">
                    <p className="font-label-md text-on-surface capitalize">{titleCase(event.status)}</p>
                    <p className="font-label-sm text-on-surface-variant">{formatDateTime(event.timestamp)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="pb-8 px-4">
          <button type="button" onClick={fetchDelivery} className="btn-outline">
            <MaterialIcon name="refresh" size={18} /> Refresh tracking
          </button>
        </div>
      </main>
    </div>
  );
}