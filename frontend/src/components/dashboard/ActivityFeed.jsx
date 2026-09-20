import { MaterialIcon } from '../ui';
import { StatusBadge } from '../ui';
import { NavLink } from 'react-router-dom';

const activityItems = [
  {
    id: 1,
    name: '50 Fresh Meal Boxes',
    location: 'Asha Shelter • Ward 4',
    status: 'in_transit',
    icon: 'lunch_dining',
    iconBg: 'bg-orange-50',
    iconColor: 'text-orange-700',
  },
  {
    id: 2,
    name: 'Winter Clothing & Blankets (30 kits)',
    location: 'Jeevan Jyoti • Tomorrow 10:00 AM',
    status: 'pickup_scheduled',
    icon: 'checkroom',
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-700',
  },
  {
    id: 3,
    name: 'Organic Rice (10 kg)',
    location: 'Community Kitchen • 17 Sep',
    status: 'delivered',
    icon: 'rice_bowl',
    iconBg: 'bg-emerald-50',
    iconColor: 'text-emerald-700',
  },
  {
    id: 4,
    name: 'Educational Textbooks (15 sets)',
    location: 'Vidya Jyoti • Request Match',
    status: 'matched',
    icon: 'menu_book',
    iconBg: 'bg-blue-50',
    iconColor: 'text-blue-700',
  },
  {
    id: 5,
    name: 'Medical First Aid Supplies',
    location: 'Red Cross Camp • Receipt Signed',
    status: 'confirmed',
    icon: 'medical_services',
    iconBg: 'bg-purple-50',
    iconColor: 'text-purple-700',
  },
];

export default function ActivityFeed({ className = "" }) {
  return (
    <section className={`flex flex-col gap-2.5 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <h3 className="font-headline-sm text-[17px] font-bold text-on-surface">Recent Activity</h3>
          <p className="font-body-sm text-[11px] text-on-surface-variant">Last 5 donation items & status progression</p>
        </div>
        <NavLink className="font-label-sm text-[12px] text-primary-container font-bold" to="/donor/dashboard/items">
          View All
        </NavLink>
      </div>
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
      <div className="flex flex-col gap-2">
        {activityItems.map((item) => (
          <div key={item.id} className="bg-surface-container-lowest p-3 rounded-xl shadow-sm border border-outline-variant/20 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className={`w-9 h-9 rounded-lg ${item.iconBg} ${item.iconColor} flex items-center justify-center shrink-0`}>
                <MaterialIcon name={item.icon} size={19} />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="font-label-lg text-[13px] text-on-surface font-bold truncate">
                  {item.name}
                </span>
                <span className="font-body-sm text-[11px] text-on-surface-variant truncate">
                  {item.location}
                </span>
              </div>
            </div>
            <StatusBadge status={item.status} size="md" />
          </div>
        ))}
      </div>
    </section>
  );
}