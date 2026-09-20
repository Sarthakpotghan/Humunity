import { Outlet } from 'react-router-dom';
import TopAppBar from './TopAppBar';
import BottomNavBar from './BottomNavBar';
import TabBar from './TabBar';

export default function DashboardLayout() {
  return (
    <div className="min-h-screen bg-surface font-body-md text-on-surface antialiased flex flex-col">
      <TopAppBar />
      <main className="flex-1 flex flex-col relative w-full pt-16 pb-28 bg-surface">
        <div className="flex flex-col w-full px-margin-mobile pt-3 pb-space-xl gap-space-lg">
          <TabBar />
          <Outlet />
        </div>
      </main>
      <BottomNavBar />
    </div>
  );
}