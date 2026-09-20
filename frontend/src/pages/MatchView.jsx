import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';

export default function MatchView() {
  const { donationId } = useParams();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchMatches();
  }, [donationId]);

  const fetchMatches = async () => {
    try {
      const response = await api.get(`/donations/${donationId}/matches`);
      setMatches(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load matches');
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (matchId) => {
    try {
      await api.patch(`/donations/matches/${matchId}/accept`);
      fetchMatches();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to accept match');
    }
  };

  const handleReject = async (matchId) => {
    try {
      await api.patch(`/donations/matches/${matchId}/reject`);
      fetchMatches();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reject match');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'accepted': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Matched NGOs</h2>

        {error && (
          <div className="mb-4 bg-red-50 text-red-600 p-4 rounded-lg text-sm">
            {error}
          </div>
        )}

        {matches.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No matches found yet. Try running the matching engine.</p>
            <button
              onClick={() => api.post(`/donations/${donationId}/match`).then(fetchMatches)}
              className="mt-4 px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-hover"
            >
              Run Matching
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((match) => (
              <div key={match.id} className="border rounded-lg p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900">NGO Request Match</h3>
                    <p className="text-gray-600 mt-1">Match Score: <span className="font-medium">{(match.score * 100).toFixed(1)}%</span></p>
                    
                    <div className="mt-4 grid grid-cols-2 md:grid-cols-7 gap-4 text-sm">
                      <div><span className="text-gray-500">Urgency:</span> <span className="font-medium">{(match.score_breakdown?.urgency?.value * 100).toFixed(0)}%</span></div>
                      <div><span className="text-gray-500">Similarity:</span> <span className="font-medium">{(match.score_breakdown?.similarity?.value * 100).toFixed(0)}%</span></div>
                      <div><span className="text-gray-500">Seasonal:</span> <span className="font-medium">{(match.score_breakdown?.seasonal?.value * 100).toFixed(0)}%</span></div>
                      <div><span className="text-gray-500">Proximity:</span> <span className="font-medium">{(match.score_breakdown?.proximity?.value * 100).toFixed(0)}%</span></div>
                      <div><span className="text-gray-500">Quantity Fit:</span> <span className="font-medium">{(match.score_breakdown?.quantity_fit?.value * 100).toFixed(0)}%</span></div>
                      <div><span className="text-gray-500">Condition:</span> <span className="font-medium">{(match.score_breakdown?.condition?.value * 100).toFixed(0)}%</span></div>
                      <div><span className="text-gray-500">Reliability:</span> <span className="font-medium">{(match.score_breakdown?.reliability?.value * 100).toFixed(0)}%</span></div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(match.status)}`}>
                      {match.status.charAt(0).toUpperCase() + match.status.slice(1)}
                    </span>
                    {match.status === 'pending' && (
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleAccept(match.id)}
                          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => handleReject(match.id)}
                          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}