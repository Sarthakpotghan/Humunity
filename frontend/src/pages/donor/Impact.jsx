import { MaterialIcon } from '../../components/ui';
import { ImpactSnapshot } from '../../components/dashboard';
import { Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const monthlyData = {
  labels: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
  datasets: [
    {
      label: 'Donations',
      data: [12, 19, 15, 25, 22, 30],
      backgroundColor: '#0F5B38',
      borderRadius: 8,
    },
  ],
};

const categoryData = {
  labels: ['Clothes', 'Stationery', 'Meals', 'Medical', 'Other'],
  datasets: [
    {
      label: 'Items',
      data: [156, 89, 67, 34, 12],
      backgroundColor: [
        '#0F5B38',
        '#005B3D',
        '#004226',
        '#005236',
        '#00412B',
      ],
      borderRadius: 8,
    },
  ],
};

const trendData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
  datasets: [
    {
      label: 'Items Donated',
      data: [45, 52, 48, 61, 55, 67, 72, 69, 78],
      borderColor: '#0F5B38',
      backgroundColor: 'rgba(15, 91, 56, 0.1)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#0F5B38',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
    },
  ],
};

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#0D1C2E',
      titleColor: '#fff',
      bodyColor: '#fff',
      padding: 12,
      cornerRadius: 8,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: '#404942', font: { family: 'Inter', size: 11 } },
    },
    y: {
      grid: { color: '#D5E3FC' },
      ticks: { color: '#404942', font: { family: 'Inter', size: 11 }, stepSize: 10 },
      beginAtZero: true,
    },
  },
};

export default function Impact() {
  return (
    <div className="flex flex-col gap-4">
      <h2 className="font-headline-md text-headline-md font-bold text-on-surface">Impact Analytics</h2>
      
      <ImpactSnapshot />
      
      <section className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm border border-outline-variant/20 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <MaterialIcon name="analytics" size={22} className="text-primary-container" />
            <h3 className="font-headline-sm text-[17px] font-bold text-on-surface">Monthly Donations</h3>
          </div>
        </div>
        <div className="h-64">
          <Bar data={monthlyData} options={chartOptions} />
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <section className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm border border-outline-variant/20 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <MaterialIcon name="category" size={22} className="text-primary-container" />
              <h3 className="font-headline-sm text-[17px] font-bold text-on-surface">By Category</h3>
            </div>
          </div>
          <div className="h-64">
              <Bar data={categoryData} options={chartOptions} />
            </div>
        </section>

        <section className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm border border-outline-variant/20 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <MaterialIcon name="show_chart" size={22} className="text-primary-container" />
              <h3 className="font-headline-sm text-[17px] font-bold text-on-surface">9-Month Trend</h3>
            </div>
          </div>
          <div className="h-64">
              <Line data={trendData} options={chartOptions} />
            </div>
        </section>
      </div>

      <section className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm border border-outline-variant/20 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <MaterialIcon name="leaderboard" size={22} className="text-primary-container" />
            <h3 className="font-headline-sm text-[17px] font-bold text-on-surface">Top NGOs Helped</h3>
          </div>
        </div>
        <div className="flex flex-col gap-3">
          {[
            { name: 'Help Kids Foundation', items: 89, location: 'Delhi', badge: 'Verified' },
            { name: 'Warm Hearts NGO', items: 67, location: 'Mumbai', badge: 'Verified' },
            { name: 'School Aid Society', items: 54, location: 'Bangalore', badge: 'Verified' },
            { name: 'Community Kitchen', items: 43, location: 'Chennai', badge: 'Verified' },
            { name: 'Red Cross Camp', items: 38, location: 'Hyderabad', badge: 'Verified' },
          ].map((ngo, index) => (
            <div key={index} className="bg-surface-container-low rounded-xl p-3 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded-xl bg-primary-container/10 text-primary-container flex items-center justify-center shrink-0">
                  <MaterialIcon name="volunteer_activism" size={20} />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="font-label-lg text-[13px] text-on-surface font-bold truncate">{ngo.name}</span>
                  <span className="font-body-sm text-[11px] text-on-surface-variant truncate">{ngo.location}</span>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="font-headline-sm text-[16px] font-bold text-on-surface">{ngo.items}</span>
                <span className="text-on-surface-variant text-sm">items</span>
                <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full font-label-sm text-[10px] font-bold">{ngo.badge}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}