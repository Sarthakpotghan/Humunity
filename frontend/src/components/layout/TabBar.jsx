import { useLocation } from 'react-router-dom';
import { NavLink } from 'react-router-dom';

const tabs = [
  { path: '/donor/dashboard', label: 'Overview', icon: 'home', isActive: true },
  { path: '/donor/dashboard/items', label: 'My Items', icon: 'inventory_2' },
  { path: '/donor/dashboard/matches', label: 'Matches', icon: 'find_in_page', badge: 4 },
  { path: '/donor/dashboard/impact', label: 'Impact', icon: 'volunteer_activism' },
];

export default function TabBar() {
  const location = useLocation();

  return (
    <nav aria-label="Donor sub-routes" className="flex items-center gap-2 overflow-x-auto py-2 no-scrollbar">
      {tabs.map((tab) => {
        const isActive = location.pathname.startsWith(tab.path);
        return (
          <NavLink
            key={tab.path}
            to={tab.path}
            className={`px-4 py-1.5 rounded-full font-label-md font-semibold shrink-0 flex items-center gap-1.5 ${
              isActive
                ? 'bg-primary-container text-on-primary shadow-sm'
                : 'bg-surface-container-lowest text-on-surface-variant hover:text-primary border border-outline-variant/30'
            }`}
          >
            {tab.icon && (
              <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-tertiary-fixed' : 'bg-transparent'}`} />
            )}
            {tab.label}
            {tab.badge && (
              <span className="px-1.5 py-0.2 bg-blue-100 text-blue-800 text-[10px] font-bold rounded-full">
                {tab.badge}
              </span>
            )}
          </NavLink>
        );
      })}
    </nav>
  );
}