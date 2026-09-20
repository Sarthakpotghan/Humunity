import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { api } from '../services/api';

const defaultPosition = [28.6139, 77.2090];

export default function MapView() {
  const { deliveryId } = useParams();
  const [delivery, setDelivery] = useState(null);
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mapCenter, setMapCenter] = useState(defaultPosition);
  const [mapZoom, setMapZoom] = useState(12);

  useEffect(() => {
    fetchDelivery();
  }, [deliveryId]);

  const fetchDelivery = async () => {
    try {
      const [deliveryRes, routeRes] = await Promise.all([
        api.get(`/deliveries/${deliveryId}`),
        api.get(`/deliveries/${deliveryId}/route`),
      ]);
      setDelivery(deliveryRes.data);
      setRoute(routeRes.data);
      if (routeRes.data?.geometry?.coordinates?.length > 0) {
        const coords = routeRes.data.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
        setMapCenter(coords[0]);
        setMapZoom(13);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load delivery');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded-lg text-sm">
        {error}
      </div>
    );
  }

  if (!delivery) {
    return <div>No delivery data</div>;
  }

  const donorLat = delivery.match?.donation?.lat;
  const donorLng = delivery.match?.donation?.lng;
  const ngoLat = delivery.match?.request?.ngo?.lat;
  const ngoLng = delivery.match?.request?.ngo?.lng;

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-500';
      case 'in_transit': return 'bg-yellow-500';
      case 'delivered': return 'bg-green-500';
      case 'confirmed': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">Delivery Tracking</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(delivery.status)}`}>
            {delivery.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          <p><strong>Mode:</strong> {delivery.mode}</p>
          <p><strong>Scheduled:</strong> {delivery.scheduled_at ? new Date(delivery.scheduled_at).toLocaleString() : 'Not scheduled'}</p>
          <p><strong>Distance:</strong> {route?.distance ? `${route.distance.toFixed(1)} km` : 'N/A'}</p>
          <p><strong>Duration:</strong> {route?.duration ? `${Math.round(route.duration)} min` : 'N/A'}</p>
        </div>
      </div>

      <div className="h-96">
        <MapContainer center={mapCenter} zoom={mapZoom} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {donorLat && donorLng && (
            <Marker position={[donorLat, donorLng]}>
              <Popup>
                <strong>Donor Location</strong><br />
                {delivery.match?.donation?.item_type} - {delivery.match?.donation?.quantity} items
              </Popup>
            </Marker>
          )}
          {ngoLat && ngoLng && (
            <Marker position={[ngoLat, ngoLng]}>
              <Popup>
                <strong>NGO Location</strong><br />
                {delivery.match?.request?.ngo?.name}
              </Popup>
            </Marker>
          )}
          {route?.geometry?.coordinates && (
            <Polyline
              positions={route.geometry.coordinates.map(([lng, lat]) => [lat, lng])}
              color="#2563eb"
              weight={4}
              opacity={0.8}
            />
          )}
        </MapContainer>
      </div>

      {delivery.events && delivery.events.length > 0 && (
        <div className="p-4 border-t">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Timeline</h3>
          <div className="space-y-4">
            {delivery.events
              .slice()
              .reverse()
              .map((event) => (
                <div key={event.id} className="flex items-start space-x-4">
                  <div className={`w-3 h-3 rounded-full mt-1.5 ${getStatusColor(event.status).replace('bg-', 'bg-')}`}></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {event.status.replace('_', ' ').toUpperCase()}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(event.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}