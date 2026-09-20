import { useState } from 'react';
import { MaterialIcon } from '../../components/ui';
import { StatusBadge } from '../../components/ui';
import { NavLink } from 'react-router-dom';

const mockDonations = [
  { id: 1, itemType: 'Jackets', category: 'clothes', quantity: 10, condition: 'good', status: 'in_transit', createdAt: '2026-09-19', size: 'M', ageGroup: '6-10', gender: 'unisex', season: 'winter' },
  { id: 2, itemType: 'Notebooks', category: 'stationery', quantity: 50, condition: 'new', status: 'accepted', createdAt: '2026-09-18', size: '100 pages', ageGroup: '10-14', gender: 'unisex', season: 'all' },
  { id: 3, itemType: 'T-Shirts', category: 'clothes', quantity: 25, condition: 'fair', status: 'listed', createdAt: '2026-09-17', size: 'L', ageGroup: 'adult', gender: 'male', season: 'summer' },
  { id: 4, itemType: 'Pencils', category: 'stationery', quantity: 200, condition: 'good', status: 'matched', createdAt: '2026-09-16', size: 'HB', ageGroup: '6-12', gender: 'unisex', season: 'all' },
  { id: 5, itemType: 'Sweaters', category: 'clothes', quantity: 15, condition: 'good', status: 'delivered', createdAt: '2026-09-10', size: 'M', ageGroup: '10-14', gender: 'female', season: 'winter' },
];

export default function MyItems() {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  const filteredDonations = mockDonations.filter(d => {
    const matchesFilter = filter === 'all' || d.status === filter;
    const matchesSearch = d.itemType.toLowerCase().includes(search.toLowerCase()) ||
      d.category.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h2 className="font-headline-md text-headline-md font-bold text-on-surface">My Items</h2>
        <NavLink 
          to="/donation/new" 
          className="flex items-center gap-1.5 px-4 py-2 bg-primary-container text-on-primary rounded-xl font-label-lg font-bold shadow-sm hover:shadow-md transition-shadow"
        >
          <MaterialIcon name="add" size={20} />
          <span>List New Item</span>
        </NavLink>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {['all', 'listed', 'matched', 'accepted', 'in_transit', 'delivered'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-full font-label-sm font-semibold transition-colors ${
              filter === f 
                ? 'bg-primary-container text-on-primary shadow-sm' 
                : 'bg-surface-container-lowest text-on-surface-variant hover:text-primary border border-outline-variant/30'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1).replace('_', ' ')}
          </button>
        ))}
      </div>

      <div className="relative mb-4">
        <MaterialIcon name="search" size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
        <input
          type="text"
          placeholder="Search items..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 bg-surface-container-lowest border border-outline-variant/30 rounded-xl font-body-md text-on-surface placeholder-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
        />
      </div>

      <div className="flex flex-col gap-3">
        {filteredDonations.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl p-8 text-center border border-outline-variant/20">
            <MaterialIcon name="inventory_2" size={48} className="text-outline mx-auto mb-3" />
            <h3 className="font-headline-sm font-bold text-on-surface mb-1">No items found</h3>
            <p className="text-on-surface-variant text-sm">Try adjusting your filters or search term</p>
          </div>
        ) : (
          filteredDonations.map((donation) => (
            <div key={donation.id} className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm border border-outline-variant/20">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <div className="w-12 h-12 rounded-xl bg-primary-container/10 text-primary-container flex items-center justify-center shrink-0">
                    <MaterialIcon name={donation.category === 'clothes' ? 'checkroom' : 'menu_book'} size={24} />
                  </div>
                  <div className="flex flex-col min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-label-lg text-[13px] text-on-surface font-bold truncate">{donation.itemType}</span>
                      <span className="px-2 py-0.5 bg-surface-container-low text-on-surface-variant rounded-md font-label-sm text-[10px]">{donation.category}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-on-surface-variant mt-1 flex-wrap">
                      <span>Qty: <span className="font-medium">{donation.quantity}</span></span>
                      <span>•</span>
                      <span>Size: <span className="font-medium">{donation.size}</span></span>
                      <span>•</span>
                      <span>{donation.ageGroup}</span>
                      <span>•</span>
                      <span>{donation.gender}</span>
                      <span>•</span>
                      <span>{donation.season}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-on-surface-variant mt-1">
                      <span>Condition: <span className="font-medium capitalize">{donation.condition}</span></span>
                      <span>•</span>
                      <span>Listed: <span className="font-medium">{new Date(donation.createdAt).toLocaleDateString()}</span></span>
                    </div>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2 shrink-0">
                  <StatusBadge status={donation.status} size="md" />
                  <div className="flex items-center gap-1.5">
                    <NavLink 
                      to={`/matches/${donation.id}`}
                      className="px-3 py-1.5 bg-primary-container text-on-primary rounded-lg font-label-sm font-bold hover:shadow-sm transition-shadow flex items-center gap-1"
                    >
                      <MaterialIcon name="find_in_page" size={16} />
                      <span className="hidden sm:inline">Match</span>
                    </NavLink>
                    <button className="px-3 py-1.5 bg-surface-container-lowest text-on-surface border border-outline-variant/30 rounded-lg font-label-sm font-medium hover:bg-surface-container-low transition-colors flex items-center gap-1">
                      <MaterialIcon name="edit" size={16} />
                      <span className="hidden sm:inline">Edit</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )))}
        </div>
      </div>
    );
}