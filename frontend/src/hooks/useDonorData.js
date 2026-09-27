import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

export function useDonorData() {
  const [data, setData] = useState({
    donations: [],
    matches: [],
    deliveries: [],
    stats: {
      totalItems: 0,
      activeDonations: 0,
      completedDeliveries: 0,
      pendingMatches: 0,
    },
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    try {
      setData(prev => ({ ...prev, loading: true, error: null }));

      const donationsRes = await api.get('/donations');
      const donations = donationsRes.data || [];

      let allMatches = [];
      for (const donation of donations) {
        try {
          const matchesRes = await api.get(`/donations/${donation.id}/matches`);
          allMatches.push(...(matchesRes.data || []));
        } catch (e) {
          // Ignore errors for individual donations
        }
      }

      let deliveries = [];
      try {
        const deliveriesRes = await api.get('/deliveries');
        deliveries = deliveriesRes.data || [];
      } catch (e) {
        // Deliveries may not exist yet
      }

      const activeStatuses = ['listed', 'matched', 'accepted', 'pickup_scheduled', 'in_transit'];
      const completedStatuses = ['delivered', 'confirmed'];

      const stats = {
        totalItems: donations.reduce((sum, d) => sum + (d.quantity || 0), 0),
        activeDonations: donations.filter(d => activeStatuses.includes(d.status)).length,
        completedDeliveries: donations.filter(d => completedStatuses.includes(d.status)).length,
        pendingMatches: allMatches.filter(m => m.status === 'pending').length,
      };

      setData({
        donations,
        matches: allMatches,
        deliveries,
        stats,
        loading: false,
        error: null,
      });
    } catch (err) {
      setData(prev => ({
        ...prev,
        loading: false,
        error: err.response?.data?.detail || 'Failed to fetch data',
      }));
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return { ...data, refetch };
}

export function useNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = useCallback(async () => {
    try {
      const res = await api.get('/notifications');
      const notifs = res.data || [];
      setNotifications(notifs);
      setUnreadCount(notifs.filter(n => !n.is_read).length);
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const markAsRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.patch('/notifications/read-all');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  };

  return { notifications, unreadCount, loading, markAsRead, markAllAsRead, refetch: fetchNotifications };
}