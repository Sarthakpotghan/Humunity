import { MaterialIcon } from '../ui';
import { NavLink } from 'react-router-dom';

export default function ImpactSnapshot({ 
  foodSaved = '86 kg',
  mealsGiven = '342',
  co2Avoided = '64 kg',
  className = ""
}) {
  return (
    <section className={`bg-surface-container-lowest rounded-2xl p-4 shadow-sm border border-outline-variant/20 flex flex-col gap-3 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <MaterialIcon name="compost" size={22} className="text-primary-container" />
          <h3 className="font-headline-sm text-[17px] font-bold text-on-surface">Impact Snapshot</h3>
        </div>
        <span className="bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full font-label-sm text-[10px] font-bold">
          Eco Verified
        </span>
      </div>
      <p className="font-body-sm text-[12px] text-on-surface-variant leading-relaxed">
        Surplus food rerouting directly avoids organic decomposition in landfills and delivers immediate nourishment to local shelters.
      </p>
      <div className="grid grid-cols-3 gap-2 pt-1">
        <div className="bg-surface-container-low rounded-xl p-2.5 flex flex-col items-center text-center">
          <span className="text-xl">🥦</span>
          <span className="font-headline-sm text-[16px] font-bold text-on-surface mt-1">{foodSaved}</span>
          <span className="font-label-sm text-[10px] text-on-surface-variant">Food Saved</span>
        </div>
        <div className="bg-surface-container-low rounded-xl p-2.5 flex flex-col items-center text-center">
          <span className="text-xl">🍲</span>
          <span className="font-headline-sm text-[16px] font-bold text-on-surface mt-1">{mealsGiven}</span>
          <span className="font-label-sm text-[10px] text-on-surface-variant">Meals Given</span>
        </div>
        <div className="bg-surface-container-low rounded-xl p-2.5 flex flex-col items-center text-center">
          <span className="text-xl">🌍</span>
          <span className="font-headline-sm text-[16px] font-bold text-on-surface mt-1">{co2Avoided}</span>
          <span className="font-label-sm text-[10px] text-on-surface-variant">CO2e Avoided</span>
        </div>
      </div>
      <div className="flex items-center justify-between pt-1 border-t border-surface-container-high text-on-surface-variant">
        <span className="font-label-sm text-[11px] flex items-center gap-1 text-primary-container font-medium">
          <MaterialIcon name="verified" size={14} />
          Verified by Humunity Protocol
        </span>
        <NavLink className="font-label-sm text-[11px] text-on-surface-variant hover:text-primary font-semibold flex items-center" to="/donor/dashboard/impact">
          View Details
          <MaterialIcon name="arrow_forward" size={13} />
        </NavLink>
      </div>
    </section>
  );
}