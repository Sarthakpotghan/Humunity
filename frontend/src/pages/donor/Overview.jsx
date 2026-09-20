import { 
  GreetingHeader, 
  QuickActionsBanner, 
  StatsCard, 
  ActiveTrackingCard, 
  ActivityFeed, 
  ImpactSnapshot 
} from '../../components/dashboard';

export default function Overview() {
  return (
    <>
      <GreetingHeader />
      <QuickActionsBanner />
      <section className="flex flex-col gap-space-xs">
        <div className="flex items-center justify-between pb-1">
          <h3 className="font-headline-sm text-[17px] font-bold text-on-surface">Overview Metrics</h3>
          <span className="font-label-sm text-[11px] text-primary-container font-bold bg-surface-container-low px-2 py-0.5 rounded-full">
            Updated Live
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <StatsCard type="totalItems" value="342" />
          <StatsCard type="activeDonations" value="3" />
          <StatsCard type="completedDeliveries" value="89" />
          <StatsCard type="pendingMatches" value="4" />
        </div>
      </section>
      <ActiveTrackingCard />
      <ActivityFeed />
      <ImpactSnapshot />
    </>
  );
}