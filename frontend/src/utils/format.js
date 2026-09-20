export function formatDate(value) {
  if (!value) return '—';
  const d = new Date(value);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

export function formatDateTime(value) {
  if (!value) return '—';
  const d = new Date(value);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) +
    ', ' +
    d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

export function timeAgo(value) {
  if (!value) return '—';
  const d = new Date(value);
  if (isNaN(d.getTime())) return '—';
  const seconds = Math.floor((Date.now() - d.getTime()) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return formatDate(value);
}

export function daysUntil(value) {
  if (!value) return null;
  const d = new Date(value);
  if (isNaN(d.getTime())) return null;
  const diff = Math.ceil((d.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
  return diff;
}

export function titleCase(value) {
  if (!value) return '';
  return String(value)
    .replace(/[_]/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function initialsOf(name = '') {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export function formatScore(value) {
  const n = Number(value);
  if (isNaN(n)) return '0%';
  return `${(n * 100).toFixed(0)}%`;
}

export function urgencyLabel(value) {
  const n = Number(value);
  const labels = { 1: 'Low', 2: 'Moderate', 3: 'Elevated', 4: 'High', 5: 'Critical' };
  return labels[n] || '—';
}

export function categoryIcon(category) {
  return category === 'stationery' ? 'menu_book' : 'checkroom';
}

export function categoryLabel(category) {
  if (category === 'stationery') return 'Educational Stationery';
  return 'Clothes';
}