const statusStyles = {
  listed: { bg: 'bg-surface-container-high', text: 'text-on-surface-variant', border: 'border-outline-variant', dot: 'bg-outline' },
  active: { bg: 'bg-tertiary-container', text: 'text-on-tertiary-container', border: 'border-tertiary-container', dot: 'bg-tertiary' },
  pending: { bg: 'bg-surface-container-high', text: 'text-on-surface-variant', border: 'border-outline-variant', dot: 'bg-outline', pulse: true },
  matched: { bg: 'bg-primary-container', text: 'text-on-primary-container', border: 'border-primary-container', dot: 'bg-primary' },
  accepted: { bg: 'bg-tertiary-container', text: 'text-on-tertiary-container', border: 'border-tertiary-container', dot: 'bg-tertiary' },
  pickup_scheduled: { bg: 'bg-status-pickup-bg', text: 'text-status-pickup-text', border: 'border-amber-200', dot: 'bg-amber-500' },
  in_transit: { bg: 'bg-status-transit-bg', text: 'text-status-transit-text', border: 'border-orange-200', dot: 'bg-orange-500' },
  delivered: { bg: 'bg-status-delivered-bg', text: 'text-status-delivered-text', border: 'border-green-200', dot: 'bg-green-500' },
  confirmed: { bg: 'bg-status-confirmed-bg', text: 'text-status-confirmed-text', border: 'border-purple-200', dot: 'bg-purple-500' },
  rejected: { bg: 'bg-error-container', text: 'text-on-error-container', border: 'border-error-container', dot: 'bg-error' },
  expired: { bg: 'bg-surface-container-highest', text: 'text-on-surface-variant', border: 'border-outline-variant', dot: 'bg-outline' },
  cancelled: { bg: 'bg-surface-container-highest', text: 'text-on-surface-variant', border: 'border-outline-variant', dot: 'bg-outline' },
  fulfilled: { bg: 'bg-tertiary-fixed', text: 'text-on-tertiary-fixed', border: 'border-tertiary-fixed', dot: 'bg-tertiary-fixed-dim' },
  closed: { bg: 'bg-surface-container-high', text: 'text-on-surface-variant', border: 'border-outline-variant', dot: 'bg-outline' },
  scheduled: { bg: 'bg-secondary-container', text: 'text-on-secondary-container', border: 'border-secondary-container', dot: 'bg-secondary' },
};

const statusLabels = {
  listed: 'Listed',
  active: 'Active',
  pending: 'Pending',
  matched: 'Matched',
  accepted: 'Accepted',
  pickup_scheduled: 'Pickup Scheduled',
  in_transit: 'In Transit',
  delivered: 'Delivered',
  confirmed: 'Confirmed',
  rejected: 'Rejected',
  expired: 'Expired',
  cancelled: 'Cancelled',
  fulfilled: 'Fulfilled',
  closed: 'Closed',
  scheduled: 'Scheduled',
};

export default function StatusBadge({
  status,
  className = '',
  showDot = false,
  size = 'md',
  ...props
}) {
  const normalized = String(status || '').toLowerCase();
  const styles = statusStyles[normalized] || statusStyles.listed;
  const label = statusLabels[normalized] || status;

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-[11px]',
    lg: 'px-3 py-1.5 text-[12px]',
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1 shrink-0
        font-label-sm font-bold rounded-full border
        ${styles.bg} ${styles.text} ${styles.border}
        ${sizeClasses[size]}
        ${className}
      `}
      {...props}
    >
      {showDot && (
        <span className={`w-1.5 h-1.5 rounded-full ${styles.dot} ${styles.pulse ? 'animate-ping-slow' : ''}`} />
      )}
      {label}
    </span>
  );
}

import MaterialIcon from './MaterialIcon';

export const StatusLegend = () => (
  <div className="p-2.5 rounded-xl bg-surface-container-lowest border border-outline-variant/20 shadow-card">
    <div className="flex items-center gap-1 mb-1.5">
      <MaterialIcon name="info" size={13} className="text-outline" />
      <span className="font-label-sm text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">
        Status Flow Reference
      </span>
    </div>
    <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 text-[10px] font-semibold">
      <span className="px-2 py-0.5 bg-surface-container-high text-on-surface-variant rounded-md shrink-0">Listed</span>
      <span className="px-2 py-0.5 bg-primary-container text-on-primary-container rounded-md shrink-0">Matched</span>
      <span className="px-2 py-0.5 bg-tertiary-container text-on-tertiary-container rounded-md shrink-0">Accepted</span>
      <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded-md shrink-0">Pickup Scheduled</span>
      <span className="px-2 py-0.5 bg-orange-100 text-orange-800 rounded-md shrink-0">In Transit</span>
      <span className="px-2 py-0.5 bg-green-100 text-green-900 rounded-md shrink-0">Delivered</span>
      <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded-md shrink-0">Confirmed</span>
    </div>
  </div>
);