import { MaterialIcon } from '../ui';
import { NavLink } from 'react-router-dom';

export default function QuickActionsBanner() {
  return (
    <section className="relative overflow-hidden rounded-2xl bg-gradient-primary text-on-primary p-space-lg shadow-md p-5">
      <div className="absolute -right-6 -bottom-8 w-36 h-36 rounded-full bg-tertiary-fixed opacity-15 blur-xl pointer-events-none" />
      <div className="absolute -top-8 -right-4 w-28 h-28 rounded-full bg-primary-fixed opacity-20 blur-lg pointer-events-none" />
      <div className="relative z-10 flex flex-col gap-3">
        <div className="inline-flex items-center gap-1.5 bg-white/15 backdrop-blur-md px-3 py-1 rounded-full w-fit">
          <MaterialIcon name="volunteer_activism" size={15} className="text-tertiary-fixed" />
          <span className="font-label-sm text-[11px] font-semibold text-on-primary uppercase tracking-wider">
            Quick Action
          </span>
        </div>
        <div className="flex flex-col gap-0.5">
          <h2 className="font-headline-sm text-headline-sm text-on-primary font-bold leading-tight">
            Ready to Share Resources?
          </h2>
          <p className="font-body-md text-body-md text-primary-fixed leading-snug">
            List surplus meals, clothing, or relief items for rapid pickup and community dispatch.
          </p>
        </div>
        <div className="flex items-center gap-2.5 pt-1">
          <NavLink
            className="flex-1 h-11 px-4 bg-surface-container-lowest hover:bg-surface-bright text-primary-container font-label-lg text-label-lg rounded-xl flex items-center justify-center gap-1.5 shadow-md font-bold active:scale-98 transition-transform"
            to="/donation/new"
          >
            <MaterialIcon name="add_circle" size={20} />
            <span>+ List New Item</span>
          </NavLink>
          <NavLink
            className="h-11 px-3.5 bg-white/10 hover:bg-white/20 backdrop-blur-md text-on-primary font-label-lg text-label-lg rounded-xl flex items-center justify-center gap-1 transition-colors border border-white/15"
            to="/donor/dashboard/matches"
          >
            <MaterialIcon name="find_in_page" size={18} />
            <span>Review Matches</span>
          </NavLink>
        </div>
      </div>
    </section>
  );
}