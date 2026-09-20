import { useAuth } from '../../context/AuthContext';
import { MaterialIcon } from '../ui';

export default function GreetingHeader() {
  const { user } = useAuth();
  const name = user?.name || 'Donor';

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <section className="flex flex-col gap-space-xs">
      <div className="flex items-start justify-between gap-space-sm">
        <div className="flex flex-col min-w-0">
          <h1 className="font-headline-md text-headline-md font-bold text-on-surface tracking-tight">
            {greeting}, {name} 👋
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant mt-0.5">
            Manage donations, track matching NGO requests, and measure relief impact.
          </p>
        </div>
        <div className="relative shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-surface-container-low border border-primary-container/15 shadow-sm">
          <MaterialIcon name="eco" size={22} className="text-primary-container" />
          <span className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-tertiary-container text-on-tertiary font-label-sm text-[9px] font-bold rounded-full flex items-center justify-center">
            4
          </span>
        </div>
      </div>
    </section>
  );
}