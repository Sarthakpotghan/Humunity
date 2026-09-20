import { MaterialIcon } from '../../components/ui';
import { StatusBadge } from '../../components/ui';

const mockMatches = [
  {
    id: 1,
    donationId: 1,
    donationName: '10 Jackets',
    ngoName: 'Help Kids Foundation',
    ngoLocation: 'Delhi, India',
    score: 74,
    status: 'accepted',
    breakdown: {
      urgency: { value: 0.8, weight: 0.3, contribution: 0.24 },
      similarity: { value: 0.77, weight: 0.2, contribution: 0.154 },
      seasonal: { value: 0.3, weight: 0.15, contribution: 0.045 },
      proximity: { value: 1.0, weight: 0.15, contribution: 0.15 },
      quantityFit: { value: 0.67, weight: 0.1, contribution: 0.067 },
      condition: { value: 0.7, weight: 0.05, contribution: 0.035 },
      reliability: { value: 1.0, weight: 0.05, contribution: 0.05 },
    },
    createdAt: '2026-09-19',
  },
  {
    id: 2,
    donationId: 1,
    donationName: '10 Jackets',
    ngoName: 'Warm Hearts NGO',
    ngoLocation: 'Mumbai, India',
    score: 68,
    status: 'pending',
    breakdown: {
      urgency: { value: 0.6, weight: 0.3, contribution: 0.18 },
      similarity: { value: 0.72, weight: 0.2, contribution: 0.144 },
      seasonal: { value: 0.5, weight: 0.15, contribution: 0.075 },
      proximity: { value: 0.8, weight: 0.15, contribution: 0.12 },
      quantityFit: { value: 0.67, weight: 0.1, contribution: 0.067 },
      condition: { value: 0.7, weight: 0.05, contribution: 0.035 },
      reliability: { value: 0.9, weight: 0.05, contribution: 0.045 },
    },
    createdAt: '2026-09-19',
  },
  {
    id: 3,
    donationId: 2,
    donationName: '50 Notebooks',
    ngoName: 'School Aid Society',
    ngoLocation: 'Bangalore, India',
    score: 82,
    status: 'pending',
    breakdown: {
      urgency: { value: 0.9, weight: 0.3, contribution: 0.27 },
      similarity: { value: 0.85, weight: 0.2, contribution: 0.17 },
      seasonal: { value: 0.8, weight: 0.15, contribution: 0.12 },
      proximity: { value: 0.9, weight: 0.15, contribution: 0.135 },
      quantityFit: { value: 0.9, weight: 0.1, contribution: 0.09 },
      condition: { value: 1.0, weight: 0.05, contribution: 0.05 },
      reliability: { value: 0.95, weight: 0.05, contribution: 0.0475 },
    },
    createdAt: '2026-09-18',
  },
];

const breakdownLabels = {
  urgency: 'Urgency',
  similarity: 'Similarity',
  seasonal: 'Seasonal',
  proximity: 'Proximity',
  quantityFit: 'Quantity Fit',
  condition: 'Condition',
  reliability: 'Reliability',
};

export default function MyMatches() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h2 className="font-headline-md text-headline-md font-bold text-on-surface">My Matches</h2>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-primary-container/20 text-primary-container rounded-full font-label-sm font-semibold">
            {mockMatches.filter(m => m.status === 'pending').length} Pending
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {mockMatches.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl p-8 text-center border border-outline-variant/20">
            <MaterialIcon name="sync_alt" size={48} className="text-outline mx-auto mb-3" />
            <h3 className="font-headline-sm font-bold text-on-surface mb-1">No matches yet</h3>
            <p className="text-on-surface-variant text-sm mb-4">Run the matching engine from your donations to find NGO matches</p>
            <button className="px-4 py-2 bg-primary-container text-on-primary rounded-xl font-label-lg font-bold shadow-sm">
              Run Matching
            </button>
          </div>
        ) : (
          mockMatches.map((match) => (
            <div key={match.id} className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/20">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900">NGO Request Match</h3>
                  <p className="text-gray-600 mt-1">Match Score: <span className="font-medium">{(match.score).toFixed(0)}%</span></p>
                  
                  <div className="mt-4 grid grid-cols-2 md:grid-cols-7 gap-4 text-sm">
                    {Object.entries(match.breakdown).map(([key, data]) => (
                      <div key={key}>
                        <span className="text-gray-500">{breakdownLabels[key] || key}:</span>
                        <span className="font-medium ml-1">{(data.value * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <StatusBadge status={match.status} size="md" />
                  {match.status === 'pending' && (
                    <div className="flex space-x-2">
                      <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium">
                        Accept
                      </button>
                      <button className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium">
                        Reject
                      </button>
                    </div>
                  )}
                  {match.status === 'accepted' && (
                    <button className="px-4 py-2 bg-primary-container text-on-primary rounded-md font-medium hover:shadow-sm transition-shadow flex items-center gap-1">
                      <MaterialIcon name="local_shipping" size={18} />
                      <span>Schedule Delivery</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          )))}
        </div>
      </div>
    );
}