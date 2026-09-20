const statusStyles = {
  listed: {
    bg: 'bg-status-listed-bg',
    text: 'text-status-listed-text',
    border: 'border-slate-200',
    dot: 'bg-slate-400',
  },
  matched: {
    bg: 'bg-status-matched-bg',
    text: 'text-status-matched-text',
    border: 'border-blue-200',
    dot: 'bg-blue-500',
  },
  accepted: {
    bg: 'bg-status-accepted-bg',
    text: 'text-status-accepted-text',
    border: 'border-emerald-200',
    dot: 'bg-emerald-500',
  },
  pickup_scheduled: {
    bg: 'bg-status-pickup-bg',
    text: 'text-status-pickup-text',
    border: 'border-amber-200',
    dot: 'bg-amber-500',
  },
  in_transit: {
    bg: 'bg-status-transit-bg',
    text: 'text-status-transit-text',
    border: 'border-orange-200',
    dot: 'bg-orange-500',
  },
  delivered: {
    bg: 'bg-status-delivered-bg',
    text: 'text-status-delivered-text',
    border: 'border-green-200',
    dot: 'bg-green-500',
  },
  confirmed: {
    bg: 'bg-status-confirmed-bg',
    text: 'text-status-confirmed-text',
    border: 'border-purple-200',
    dot: 'bg-purple-500',
  },
  rejected: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    dot: 'bg-red-500',
  },
  expired: {
    bg: 'bg-slate-100',
    text: 'text-slate-600',
    border: 'border-slate-200',
    dot: 'bg-slate-400',
  },
};

const statusLabels = {
  listed: 'Listed',
  matched: 'Matched',
  accepted: 'Accepted',
  pickup_scheduled: 'Pickup Scheduled',
  in_transit: 'In Transit',
  delivered: 'Delivered',
  confirmed: 'Confirmed',
  rejected: 'Rejected',
  expired: 'Expired',
};

export default function StatusBadge({ 
  status, 
  className = "", 
  showDot = false,
  size = 'md',
  ...props 
}) {
  const styles = statusStyles[status] || statusStyles.listed;
  const label = statusLabels[status] || status;
  
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
        <span className={`w-1.5 h-1.5 rounded-full ${styles.dot} animate-ping`} />
      )}
      {label}
    </span>
  );
}

import MaterialIcon from './MaterialIcon';

export const StatusLegend = () => (
  <div className="p-2.5 rounded-xl bg-surface-container-lowest border border-outline-variant/20 shadow-2xs">
    <div className="flex items-center gap-1 mb-1.5">
      <MaterialIcon name="info" size={13} className="text-outline" />
      <span className="font-label-sm text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">
        Status Flow Reference
      </span>
    </div>
    <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 text-[10px] font-semibold">
      <span className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded-md shrink-0">Gray: Listed</span>
      <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-md shrink-0">Blue: Matched</span>
      <span className="px-2 py-0.5 bg-emerald-50 text-emerald-800 rounded-md shrink-0">Green: Accepted</span>
      <span className="px-2 py-0.5 bg-amber-50 text-amber-800 rounded-md shrink-0">Yellow: Pickup Scheduled</span>
      <span className="px-2 py-0.5 bg-orange-100 text-orange-800 rounded-md shrink-0">Orange: In Transit</span>
      <span className="px-2 py-0.5 bg-green-100 text-green-900 rounded-md shrink-0">Green: Delivered</span>
      <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded-md shrink-0">Purple: Confirmed</span>
    </div>
  </div>
);