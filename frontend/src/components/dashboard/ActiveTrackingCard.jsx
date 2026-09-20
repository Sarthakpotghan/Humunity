import { MaterialIcon } from '../ui';
import { NavLink } from 'react-router-dom';

export default function ActiveTrackingCard({ 
  batchId = 'HM-8842',
  itemName = '50 Fresh Meal Boxes',
  destination = 'Asha Foundation Shelter, Ward 4',
  status = 'in_transit',
  volunteerName = 'Volunteer Vikram',
  eta = '18 mins',
  distance = '3.2 km',
  currentStep = 3,
  onTrackClick,
  className = ""
}) {
  const steps = [
    { label: 'Scheduled', icon: 'check', completed: currentStep >= 1, active: currentStep === 1 },
    { label: 'Picked Up', icon: 'check', completed: currentStep >= 2, active: currentStep === 2 },
    { label: 'In Transit', icon: 'local_shipping', completed: currentStep >= 3, active: currentStep === 3 },
    { label: 'Delivered', icon: 'flag', completed: currentStep >= 4, active: currentStep === 4 },
  ];

  const statusColors = {
    in_transit: { 
      bg: 'bg-amber-500/10', 
      text: 'text-amber-800', 
      border: 'border-amber-500/20',
      iconColor: 'text-amber-600',
      badgeBg: 'bg-amber-500',
      stepColor: 'bg-amber-500',
    },
    pickup_scheduled: {
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-500/20',
      iconColor: 'text-amber-600',
      badgeBg: 'bg-amber-500',
      stepColor: 'bg-amber-500',
    },
    delivered: {
      bg: 'bg-emerald-50',
      text: 'text-emerald-800',
      border: 'border-emerald-500/20',
      iconColor: 'text-emerald-600',
      badgeBg: 'bg-emerald-500',
      stepColor: 'bg-emerald-500',
    },
  };

  const colors = statusColors[status] || statusColors.in_transit;

  return (
    <section className={`flex flex-col gap-space-xs ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <h3 className="font-headline-sm text-[17px] font-bold text-on-surface">Active Tracking</h3>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-orange-50 text-orange-800 rounded-full font-label-sm text-[11px] font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-ping" />
            Live Dispatch
          </span>
        </div>
        <NavLink 
          className="font-label-sm text-label-sm text-primary-container font-semibold flex items-center" 
          to="/donor/dashboard/items"
        >
          View All
          <MaterialIcon name="chevron_right" size={15} />
        </NavLink>
      </div>
      <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm border border-outline-variant/20 flex flex-col gap-3.5">
        <div className="flex items-start justify-between gap-space-sm">
          <div className="flex flex-col min-w-0">
            <span className="font-label-sm text-[11px] text-primary-container font-bold tracking-wider uppercase">
              BATCH #{batchId}
            </span>
            <h4 className="font-headline-sm text-[16px] font-bold text-on-surface truncate mt-0.5">
              {itemName}
            </h4>
            <p className="font-body-sm text-[12px] text-on-surface-variant flex items-center gap-1 mt-0.5">
              <MaterialIcon name="location_on" size={14} className="text-outline" />
              {destination}
            </p>
          </div>
          <span className={`shrink-0 inline-flex items-center gap-1 ${colors.bg} ${colors.text} ${colors.border} px-2.5 py-1 rounded-full font-label-sm text-[11px] font-bold`}>
            <MaterialIcon name="local_shipping" size={13} className={colors.iconColor} />
            {status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </span>
        </div>
        <div className="py-1">
          <div className="relative flex items-center justify-between w-full">
            <div className="absolute top-1/2 left-4 right-4 -translate-y-1/2 h-1 bg-surface-container -z-0" />
            <div className="absolute top-1/2 left-4 w-2/3 -translate-y-1/2 h-1 bg-[#0F5B38] -z-0" />
            {steps.map((step, index) => (
              <div key={index} className="relative z-10 flex flex-col items-center">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center shadow-xs ${
                  step.completed 
                    ? (step.active ? `${colors.stepColor} text-white` : 'bg-[#0F5B38] text-white')
                    : 'bg-surface-container text-outline'
                } ${step.active ? 'w-7 h-7' : ''}`}>
                  <MaterialIcon name={step.icon} size={step.active ? 15 : 13} />
                </div>
                <span className={`font-label-sm text-[10px] font-semibold mt-1 ${
                  step.active ? (step.label === 'In Transit' ? 'text-amber-700' : 'text-on-surface') : 'text-outline'
                } ${step.completed && !step.active ? 'text-on-surface' : ''}`}>
                  {step.label}
                </span>
              </div>
            ))}
          </div>
        </div>
        <div className="flex items-center justify-between pt-1 bg-surface-container-low/80 p-3 rounded-xl border border-surface-container-high">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-surface-container-lowest flex items-center justify-center text-primary-container shrink-0 shadow-xs">
              <MaterialIcon name="two_wheeler" size={18} />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-label-sm text-[12px] text-on-surface font-bold truncate">
                {volunteerName}
              </span>
              <span className="font-body-sm text-[11px] text-secondary font-medium">
                ETA {eta} • {distance} away
              </span>
            </div>
          </div>
          <button 
            className="px-3 py-1.5 bg-primary-container text-on-primary rounded-lg font-label-sm text-[12px] font-bold active:scale-95 transition-transform flex items-center gap-1 shadow-xs"
            onClick={onTrackClick}
          >
            <MaterialIcon name="near_me" size={14} />
            <span>Track Live</span>
          </button>
        </div>
      </div>
    </section>
  );
}