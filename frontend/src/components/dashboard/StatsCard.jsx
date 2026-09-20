import { MaterialIcon } from '../ui';

const cardConfigs = {
  totalItems: {
    label: 'Total Items Donated',
    icon: 'inventory_2',
    iconBg: 'bg-surface-container-low',
    iconColor: 'text-primary-container',
    valueColor: 'text-on-surface',
    trendColor: 'text-primary-container',
    trendIcon: 'trending_up',
    trendText: '+18 this month',
  },
  activeDonations: {
    label: 'Active Donations',
    icon: 'local_shipping',
    iconBg: 'bg-amber-50',
    iconColor: 'text-secondary',
    valueColor: 'text-on-surface',
    trendColor: 'text-secondary',
    trendIcon: '',
    trendText: 'In-Flight / Scheduled',
    dotColor: 'bg-secondary-container',
  },
  completedDeliveries: {
    label: 'Completed Deliveries',
    icon: 'task_alt',
    iconBg: 'bg-emerald-50',
    iconColor: 'text-emerald-700',
    valueColor: 'text-on-surface',
    trendColor: 'text-on-surface-variant',
    trendIcon: '',
    trendText: 'Successful drops',
  },
  pendingMatches: {
    label: 'Pending Matches',
    icon: 'sync_alt',
    iconBg: 'bg-blue-50',
    iconColor: 'text-blue-700',
    valueColor: 'text-blue-700',
    trendColor: 'text-blue-600',
    trendIcon: '',
    trendText: 'Awaiting confirmation',
  },
};

export default function StatsCard({ type, value, className = "" }) {
  const config = cardConfigs[type];
  if (!config) return null;

  return (
    <div className={`bg-surface-container-lowest p-3.5 rounded-2xl shadow-sm border border-outline-variant/20 flex flex-col justify-between ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="font-label-sm text-[12px] text-on-surface-variant font-medium">
          {config.label}
        </span>
        <div className={`w-7 h-7 rounded-lg ${config.iconBg} ${config.iconColor} flex items-center justify-center`}>
          <MaterialIcon name={config.icon} size={17} />
        </div>
      </div>
      <div>
        <div className={`font-headline-lg text-[26px] ${config.valueColor} font-extrabold tracking-tight`}>
          {value}
        </div>
        <div className="flex items-center gap-1 mt-0.5">
          {config.trendIcon && (
            <MaterialIcon name={config.trendIcon} size={14} className={config.trendColor} />
          )}
          {config.dotColor && (
            <span className={`w-1.5 h-1.5 rounded-full ${config.dotColor}`} />
          )}
          <span className={`font-label-sm text-[11px] font-semibold ${config.trendColor} truncate`}>
            {config.trendText}
          </span>
        </div>
      </div>
    </div>
  );
}