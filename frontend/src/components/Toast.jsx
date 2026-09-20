import { MaterialIcon } from './ui';

export default function Toast({ message, tone = 'success', onClose }) {
  if (!message) return null;
  const styles = {
    success: 'bg-tertiary-container text-on-tertiary-container',
    error: 'bg-error-container text-on-error-container',
    info: 'bg-primary-container text-on-primary-container',
    critical: 'bg-error text-on-error',
  };
  const icons = { success: 'check_circle', error: 'error', info: 'info', critical: 'warning' };

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] animate-fade-up">
      <div className={`flex items-center gap-2.5 px-5 py-3 rounded-full shadow-elevated ${styles[tone] || styles.info}`}>
        <MaterialIcon name={icons[tone] || 'info'} size={20} />
        <span className="font-label-md">{message}</span>
        <button type="button" onClick={onClose} className="ml-1 opacity-70 hover:opacity-100" aria-label="Dismiss">
          <MaterialIcon name="close" size={18} />
        </button>
      </div>
    </div>
  );
}