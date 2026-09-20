import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../hooks/useDonorData';
import { MaterialIcon, Logo, Avatar } from '../ui';
import { timeAgo } from '../../utils/format';

export default function TopAppBar({ subtitle }) {
  const { user, logout } = useAuth();
  const { notifications, unreadCount, markAllAsRead, refetch } = useNotifications();
  const [openPanel, setOpenPanel] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const panelRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setOpenPanel(null);
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleLogout = () => {
    setMenuOpen(false);
    logout();
    navigate('/login', { replace: true });
  };

  const switchRoleHome = () => {
    setMenuOpen(false);
    navigate(user?.role === 'ngo' ? '/ngo/dashboard' : user?.role === 'admin' ? '/admin/dashboard' : '/donor/dashboard');
  };

  return (
    <header className="fixed top-0 w-full z-50 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl border-b border-surface-container-high shadow-card">
      <div className="h-16 px-gutter-mobile flex items-center justify-between gap-space-sm">
        <button type="button" onClick={switchRoleHome} className="flex items-center gap-space-xs min-w-0" aria-label="Go to dashboard">
          <Logo size="md" />
          {subtitle && (
            <span className="hidden sm:inline font-label-sm text-on-surface-variant truncate">/ {subtitle}</span>
          )}
        </button>
        <div className="flex items-center gap-space-xs shrink-0">
          <div className="relative" ref={panelRef}>
            <button
              aria-label="Notifications"
              className="relative icon-btn"
              type="button"
              onClick={() => { setMenuOpen(false); setOpenPanel(openPanel === 'notifications' ? null : 'notifications'); }}
            >
              <MaterialIcon name="notifications" size={22} />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 min-w-[18px] h-[18px] px-1 bg-error text-on-error rounded-full font-label-sm text-[10px] font-bold flex items-center justify-center ring-2 ring-surface-container-lowest">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {openPanel === 'notifications' && (
              <div className="absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] rounded-lg bg-surface-container-lowest shadow-elevated border border-outline-variant/30 overflow-hidden animate-fade-up">
                <div className="flex items-center justify-between px-4 py-3 border-b border-outline-variant/30">
                  <span className="font-label-lg text-on-surface">Notifications</span>
                  {unreadCount > 0 && (
                    <button type="button" onClick={markAllAsRead} className="btn-ghost px-2 py-1 text-primary">
                      Mark all read
                    </button>
                  )}
                </div>
                <div className="max-h-80 overflow-y-auto no-scrollbar">
                  {notifications.length === 0 && (
                    <div className="px-4 py-8 text-center text-on-surface-variant text-body-sm">
                      No notifications yet
                    </div>
                  )}
                  {notifications.slice(0, 20).map((n) => (
                    <div key={n.id} className={`flex gap-3 px-4 py-3 border-b border-outline-variant/20 ${n.is_read ? '' : 'bg-primary-fixed/20'}`}>
                      <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${n.is_read ? 'bg-outline' : 'bg-primary'}`} />
                      <div className="flex flex-col gap-0.5 min-w-0">
                        <p className="text-body-sm text-on-surface">{n.message}</p>
                        <span className="font-label-sm text-on-surface-variant">{timeAgo(n.created_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="px-4 py-2">
                  <button type="button" onClick={() => refetch()} className="w-full py-2 flex items-center justify-center gap-1 font-label-md text-on-surface-variant hover:text-primary">
                    <MaterialIcon name="refresh" size={16} /> Refresh
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="relative" ref={panelRef}>
            <button
              aria-label="Account menu"
              type="button"
              onClick={() => { setOpenPanel(null); setMenuOpen(!menuOpen); }}
              className="rounded-full"
            >
              <Avatar name={user?.name} size={36} />
            </button>

            {menuOpen && (
              <div className="absolute right-0 mt-2 w-56 rounded-lg bg-surface-container-lowest shadow-elevated border border-outline-variant/30 overflow-hidden animate-fade-up">
                <div className="px-4 py-3 border-b border-outline-variant/30">
                  <p className="font-label-md text-on-surface truncate">{user?.name}</p>
                  <p className="font-label-sm text-on-surface-variant truncate capitalize">{user?.role}</p>
                </div>
                <div className="py-1">
                  <button type="button" onClick={switchRoleHome} className="w-full text-left px-4 py-2 text-body-md text-on-surface hover:bg-surface-container-low">
                    My Dashboard
                  </button>
                  <button type="button" onClick={handleLogout} className="w-full text-left px-4 py-2 text-body-md text-error hover:bg-error-container/50">
                    Log out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}