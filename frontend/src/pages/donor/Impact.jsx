import { useDonorData } from '../../hooks/useDonorData';
import { StatusBadge, MaterialIcon } from '../../components/ui';
import { formatDate, titleCase, formatScore } from '../../utils/format';

export default function Impact() {
  const { donations, matches, stats, loading, error } = useDonorData();

  const categoryTotals = donations.reduce((acc, d) => {
    acc[d.category] = (acc[d.category] || 0) + (d.quantity || 0);
    return acc;
  }, {});

  const categoryList = Object.entries(categoryTotals).sort((a, b) => b[1] - a[1]);
  const categoryMax = Math.max(1, ...categoryList.map(([, v]) => v));

  const statusCounts = donations.reduce((acc, d) => {
    acc[d.status] = (acc[d.status] || 0) + 1;
    return acc;
  }, {});

  const recentMatches = [...matches].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 6);

  if (loading && donations.length === 0) {
    return <div className="flex items-center justify-center h-64 text-on-surface-variant">Loading...</div>;
  }

  return (
    <div className="flex flex-col gap-5">
      <h1 className="font-headline-md text-headline-md text-on-surface">Impact Analytics</h1>

      {error && (
        <div className="bg-error-container text-on-error-container rounded-lg p-4 font-body-sm">{error}</div>
      )}

      <section className="grid grid-cols-3 gap-3">
        <div className="bg-tertiary-container rounded-lg p-4 flex flex-col gap-1">
          <span className="font-display text-display-lg text-on-tertiary-container">{stats.totalItems}</span>
          <span className="font-label-sm text-on-tertiary-container">Items Donated</span>
        </div>
        <div className="bg-primary-container rounded-lg p-4 flex flex-col gap-1">
          <span className="font-display text-display-lg text-on-primary-container">{stats.completedDeliveries}</span>
          <span className="font-label-sm text-on-primary-container">Deliveries Completed</span>
        </div>
        <div className="bg-secondary-container rounded-lg p-4 flex flex-col gap-1">
          <span className="font-display text-display-lg text-on-secondary-container">{stats.activeDonations}</span>
          <span className="font-label-sm text-on-secondary-container">Active Donations</span>
        </div>
      </section>

      <section className="bg-surface-container-lowest rounded-2xl p-5 shadow-card border border-outline-variant/20">
        <div className="flex items-center gap-1.5 mb-4">
          <MaterialIcon name="category" size={20} className="text-primary" />
          <h3 className="font-headline-sm text-headline-sm text-on-surface">Items by Category</h3>
        </div>
        {categoryList.length === 0 ? (
          <p className="py-6 text-center font-body-sm text-on-surface-variant">No donations listed yet</p>
        ) : (
          <div className="flex flex-col gap-3">
            {categoryList.map(([cat, total]) => (
              <div key={cat} className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-label-md text-on-surface capitalize">{cat}</span>
                  <span className="font-label-md text-on-surface-variant">{total} items</span>
                </div>
                <div className="h-2.5 rounded-full bg-surface-container-high overflow-hidden">
                  <div className="h-full rounded-full bg-tertiary" style={{ width: `${(total / categoryMax) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="bg-surface-container-lowest rounded-2xl p-5 shadow-card border border-outline-variant/20">
        <div className="flex items-center gap-1.5 mb-4">
          <MaterialIcon name="inventory_2" size={20} className="text-primary" />
          <h3 className="font-headline-sm text-headline-sm text-on-surface">Donation Status</h3>
        </div>
        {Object.keys(statusCounts).length === 0 ? (
          <p className="py-6 text-center font-body-sm text-on-surface-variant">No donations yet</p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {Object.entries(statusCounts).map(([status, count]) => (
              <span key={status} className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-container-low">
                <StatusBadge status={status} size="sm" />
                <span className="font-label-md font-bold text-on-surface">{count}</span>
              </span>
            ))}
          </div>
        )}
      </section>

      <section className="bg-surface-container-lowest rounded-2xl p-5 shadow-card border border-outline-variant/20">
        <div className="flex items-center gap-1.5 mb-4">
          <MaterialIcon name="volunteer_activism" size={20} className="text-primary" />
          <h3 className="font-headline-sm text-headline-sm text-on-surface">Recent Matches</h3>
        </div>
        {recentMatches.length === 0 ? (
          <p className="py-6 text-center font-body-sm text-on-surface-variant">No matches yet</p>
        ) : (
          <div className="flex flex-col gap-2">
            {recentMatches.map((m) => {
              const donation = donations.find((x) => x.id === m.donation_id);
              return (
                <div key={m.id} className="bg-surface-container-low rounded-lg p-3 flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-primary-container/50 text-on-primary-container flex items-center justify-center shrink-0">
                    <MaterialIcon name="volunteer_activism" size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-label-md text-on-surface truncate">
                      {donation ? titleCase(donation.item_type) : `Donation #${m.donation_id}`}
                    </p>
                    <p className="font-label-sm text-on-surface-variant">{formatDate(m.created_at)} · {formatScore(m.score)}</p>
                  </div>
                  <StatusBadge status={m.status} size="sm" />
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}