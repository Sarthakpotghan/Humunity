import { useLocation } from 'react-router-dom';
import { MaterialIcon } from '../ui';
import { NavLink } from 'react-router-dom';

const navItems = [
  { path: '/donor/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { path: '/donor/dashboard/items', label: 'Items', icon: 'inventory_2' },
  { path: '/donation/new', label: '+ List', icon: 'add', isFab: true },
  { path: '/donor/dashboard/matches', label: 'Matches', icon: 'sync_alt', badge: 4 },
  { path: '/donor/dashboard/impact', label: 'Impact', icon: 'volunteer_activism' },
];

export default function BottomNavBar() {
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 w-full z-50 pb-safe bg-surface-container-lowest/95 backdrop-blur-xl border-t border-surface-container-high shadow-[0_-2px_12px_rgba(15,91,56,0.06)]">
      <div className="relative flex items-center justify-around h-16 px-1">
        {navItems.map((item) => {
          if (item.isFab) {
            return (
              <div key={item.path} className="relative flex flex-col items-center -top-4">
                <NavLink
                  aria-label="List New Item"
                  to={item.path}
                  className="w-13 h-13 p-3.5 rounded-full bg-primary-container text-on-primary flex items-center justify-center shadow-elevated active:scale-95 transition-transform"
                >
                  <MaterialIcon name={item.icon} size={28} />
                </NavLink>
                <span className="font-label-sm text-[10px] font-bold text-primary-container mt-1">
                  {item.label}
                </span>
              </div>
            );
          }

          const isActive = location.pathname.startsWith(item.path);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`relative flex flex-col items-center justify-center min-w-[54px] h-12 transition-colors ${
                isActive 
                  ? 'text-primary-container font-bold' 
                  : 'text-on-surface-variant hover:text-primary'
              }`}
            >
              <MaterialIcon name={item.icon} size={22} />
              {item.badge && (
                <span className="absolute top-2 right-3 w-4 h-4 bg-blue-600 text-white rounded-full font-label-sm text-[9px] font-bold flex items-center justify-center">
                  {item.badge}
                </span>
              )}
              <span className="font-label-sm text-[11px] mt-0.5">
                {item.label}
              </span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}