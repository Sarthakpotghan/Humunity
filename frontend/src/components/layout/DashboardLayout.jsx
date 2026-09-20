import { Outlet } from 'react-router-dom';
import TopAppBar from './TopAppBar';
import BottomNavBar from './BottomNavBar';
import { useDonorData } from '../../hooks/useDonorData';

export default function DashboardLayout() {
  const { matches } = useDonorData();
  const pendingMatches = matches.filter((m) => m.status === 'pending').length;

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface antialiased flex flex-col">
      <TopAppBar />
      <main className="flex-1 flex flex-col relative w-full pt-16 pb-28 bg-surface">
        <div className="flex flex-col w-full max-w-5xl mx-auto px-margin-mobile pt-4 pb-space-xl gap-space-lg">
          <Outlet />
        </div>
      </main>
      <BottomNavBar matchesCount={pendingMatches} />
    </div>
  );
}