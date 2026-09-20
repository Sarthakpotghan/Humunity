import { useAuth } from '../../context/AuthContext';
import { MaterialIcon, Logo } from '../ui';

export default function TopAppBar() {
  const { user } = useAuth();

  return (
    <header className="fixed top-0 w-full z-50 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl border-b border-surface-container-high/60 shadow-card">
      <div className="h-16 px-gutter-mobile flex items-center justify-between gap-space-sm">
        <div className="flex items-center gap-space-xs min-w-0">
          <Logo size="md" />
        </div>
        <div className="flex items-center gap-space-xs shrink-0">
          <button 
            aria-label="Search" 
            className="w-10 h-10 flex items-center justify-center rounded-full text-on-surface-variant hover:bg-surface-container-low hover:text-primary transition-colors" 
            type="button"
          >
            <MaterialIcon name="search" size={22} />
          </button>
          <button 
            aria-label="Notifications" 
            className="relative w-10 h-10 flex items-center justify-center rounded-full text-on-surface-variant hover:bg-surface-container-low hover:text-primary transition-colors" 
            type="button"
          >
            <MaterialIcon name="notifications" size={22} />
            <span className="absolute top-2 right-2 w-2 h-2 bg-secondary-container rounded-full ring-2 ring-surface-container-lowest" />
          </button>
          <div className="pl-1">
            <img 
              alt={`${user?.name || 'User'} Profile Avatar`} 
              className="w-9 h-9 rounded-full object-cover ring-2 ring-primary-container/20 shadow-sm" 
              src={user?.avatar || "https://lh3.googleusercontent.com/aida/AEtjO1XJzuPWWc6x7tTuFnwnfR0XA7e5LhzsZ58qnergQFFFrn4bXRinlgjRXpMjvfy3cFmVRJKpp-sRAfavFIjs6gxVhUYQGdjy1XIj6yVuNc7lJY-4ioOHPtyQVPNFdDC-J8cFrY7udQIOKKaFlUf1Tm6uGzwPSHbSiox1b5lE2vXLxCvl3ifZ9msiusD8gvqcKhubSDTNpn1yssTqG7hiZTG78jyyXty0H2cYgkFbkIs5VLVxBFAqqfqwRIc"}
            />
          </div>
        </div>
      </div>
    </header>
  );
}