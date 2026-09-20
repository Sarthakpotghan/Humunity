import { useDonorData, useNotifications } from '../../hooks/useDonorData';
import { useAuth } from '../../context/AuthContext';
import { MaterialIcon, StatusBadge, Avatar } from '../../components/ui';
import { NavLink, useNavigate } from 'react-router-dom';
import { formatDate, timeAgo, categoryIcon, categoryLabel, titleCase } from '../../utils/format';

const statMeta = {
  totalItems: { label: 'Total Items', icon: 'inventory_2', tone: 'tertiary' },
  activeDonations: { label: 'Active Donations', icon: 'campaign', tone: 'primary' },
  completedDeliveries: { label: 'Completed', icon: 'task_alt', tone: 'secondary' },
  pendingMatches: { label: 'Pending Matches', icon: 'sync_alt', tone: 'primary' },
};

export default function Overview() {
  const { user } = useAuth();
  const { donations, matches, stats, loading, refetch } = useDonorData();
  const { notifications, unreadCount } = useNotifications();
  const navigate = useNavigate();

  const greeting = (() => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  })();

  const firstName = user?.name?.split(' ')[0] || 'there';
  const recentDonations = [...donations].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 4);
  const recentMatches = [...matches].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 4);

  return (
    <div className="flex flex-col gap-6">
      <section className="flex items-center gap-4">
        <Avatar name={user?.name} size={52} />
        <div className="min-w-0">
          <h1 className="font-headline-lg text-headline-lg text-on-surface">{greeting}, {firstName}</h1>
          <p className="font-body-sm text-on-surface-variant">Here is what is happening with your donations</p>
        </div>
        <button type="button" onClick={refetch} className="icon-btn ml-auto" aria-label="Refresh">
          <MaterialIcon name="refresh" size={20} />
        </button>
      </section>

      <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {Object.entries(statMeta).map(([key, meta]) => (
          <div key={key} className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-4 flex flex-col gap-2">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${meta.tone === 'tertiary' ? 'bg-tertiary-container text-on-tertiary-container' : meta.tone === 'primary' ? 'bg-primary-container text-on-primary-container' : 'bg-secondary-container text-on-secondary-container'}`}>
              <MaterialIcon name={meta.icon} size={22} />
            </div>
            <span className="font-display text-display-lg text-on-surface">{stats[key] ?? 0}</span>
            <span className="font-label-sm text-on-surface-variant">{meta.label}</span>
          </div>
        ))}
      </section>

      <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-5 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h2 className="font-headline-sm text-headline-sm text-on-surface">Quick Actions</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button type="button" onClick={() => navigate('/donation/new')} className="flex flex-col items-center gap-2 p-4 rounded-full bg-primary text-on-primary shadow-sm hover:opacity-90">
            <MaterialIcon name="add_circle" size={26} />
            <span className="font-label-md">List New Item</span>
          </button>
          <button type="button" onClick={() => navigate('/donor/dashboard/items')} className="flex flex-col items-center gap-2 p-4 rounded-full bg-surface-container-low text-on-surface-variant hover:bg-surface-container-high">
            <MaterialIcon name="inventory_2" size={26} />
            <span className="font-label-md">My Items</span>
          </button>
          <button type="button" onClick={() => navigate('/donor/dashboard/matches')} className="flex flex-col items-center gap-2 p-4 rounded-full bg-surface-container-low text-on-surface-variant hover:bg-surface-container-high">
            <MaterialIcon name="sync_alt" size={26} />
            <span className="font-label-md">Review Matches</span>
          </button>
          <button type="button" onClick={() => navigate('/donor/dashboard/impact')} className="flex flex-col items-center gap-2 p-4 rounded-full bg-surface-container-low text-on-surface-variant hover:bg-surface-container-high">
            <MaterialIcon name="volunteer_activism" size={26} />
            <span className="font-label-md">Your Impact</span>
          </button>
        </div>
      </section>

      <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-5 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h2 className="font-headline-sm text-headline-sm text-on-surface">Recent Donations</h2>
          <NavLink to="/donor/dashboard/items" className="font-label-md text-primary hover:underline">
            View all
          </NavLink>
        </div>
        {loading ? (
          <div className="py-8 text-center text-on-surface-variant">Loading donations...</div>
        ) : recentDonations.length === 0 ? (
          <div className="py-10 text-center">
            <MaterialIcon name="inventory_2" size={40} className="text-outline mx-auto mb-3" />
            <p className="font-body-md text-on-surface-variant mb-3">You have not listed any donations yet</p>
            <button type="button" onClick={() => navigate('/donation/new')} className="btn-primary">
              <MaterialIcon name="add" size={18} /> List your first item
            </button>
          </div>
        ) : (
          recentDonations.map((d) => (
            <div key={d.id} className="flex items-center gap-3 rounded-lg p-3 hover:bg-surface-container-low transition-colors">
              <div className="w-11 h-11 rounded-full bg-primary-container/50 text-on-primary-container flex items-center justify-center shrink-0">
                <MaterialIcon name={categoryIcon(d.category)} size={22} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-label-lg text-on-surface truncate capitalize">{d.item_type}</p>
                <p className="font-label-sm text-on-surface-variant">
                  {categoryLabel(d.category)} · Qty {d.quantity} · Listed {formatDate(d.created_at)}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <StatusBadge status={d.status} size="sm" />
                {d.status === 'listed' && (
                  <button type="button" onClick={() => navigate(`/matches/${d.id}`)} className="btn-ghost px-2 py-1 text-primary">
                    Manage
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-5 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">Updates</h2>
            {unreadCount > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-error-container text-on-error-container font-label-sm font-bold">{unreadCount} new</span>
            )}
          </div>
          {notifications.length === 0 ? (
            <p className="py-6 text-center font-body-sm text-on-surface-variant">No updates yet</p>
          ) : (
            notifications.slice(0, 5).map((n) => (
              <div key={n.id} className="flex gap-3">
                <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${n.is_read ? 'bg-outline' : 'bg-primary'}`} />
                <div className="flex flex-col gap-0.5 min-w-0">
                  <p className="font-body-sm text-on-surface">{n.message}</p>
                  <span className="font-label-sm text-on-surface-variant">{timeAgo(n.created_at)}</span>
                </div>
              </div>
            ))
          )}
        </section>

        <section className="bg-surface-container-lowest rounded-lg shadow-card border border-outline-variant/20 p-5 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">Latest Matches</h2>
            <NavLink to="/donor/dashboard/matches" className="font-label-md text-primary hover:underline">View all</NavLink>
          </div>
          {loading ? (
            <div className="py-8 text-center text-on-surface-variant">Loading matches...</div>
          ) : recentMatches.length === 0 ? (
            <p className="py-6 text-center font-body-sm text-on-surface-variant">
              No matches yet. {donations.length > 0 ? 'Run matching from a listed donation.' : 'List an item to start getting matches.'}
            </p>
          ) : (
            recentMatches.map((m) => {
              const donation = donations.find((x) => x.id === m.donation_id);
              return (
                <div key={m.id} className="flex items-center gap-3 rounded-lg p-3 hover:bg-surface-container-low transition-colors">
                  <div className="w-11 h-11 rounded-full bg-secondary-container/50 text-on-secondary-container flex items-center justify-center shrink-0">
                    <MaterialIcon name="volunteer_activism" size={20} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-label-lg text-on-surface truncate">{donation?.item_type ? titleCase(donation.item_type) : `Donation #${m.donation_id}`}</p>
                    <div className="flex items-center gap-1.5">
                      <div className="h-1.5 flex-1 max-w-[120px] rounded-full bg-surface-container-high overflow-hidden">
                        <div className="h-full rounded-full bg-tertiary" style={{ width: `${(m.score || 0) * 100}%` }} />
                      </div>
                      <span className="font-label-sm text-on-surface-variant">{(m.score || 0) * 100 >= 1 ? Math.round(m.score * 100) : Math.round((m.score || 0) * 100)}%</span>
                    </div>
                  </div>
                  <StatusBadge status={m.status} size="sm" />
                </div>
              );
            })
          )}
        </section>
      </div>
    </div>
  );
}