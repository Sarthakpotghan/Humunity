const INITIAL_COLORS = [
  'bg-primary-container text-on-primary-container',
  'bg-secondary-container text-on-secondary-container',
  'bg-tertiary-container text-on-tertiary-container',
];

function initialsOf(name = '') {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export default function Avatar({
  name = '',
  size = 36,
  className = '',
  ring = true,
  ...props
}) {
  const initials = initialsOf(name);
  const colorIndex = (name.split('').reduce((a, c) => a + c.charCodeAt(0), 0) || 0) % INITIAL_COLORS.length;
  const color = INITIAL_COLORS[colorIndex];

  return (
    <span
      className={`inline-flex items-center justify-center rounded-full font-headline-sm font-bold shrink-0 ${color} ${
        ring ? 'ring-2 ring-primary-container/20 ring-offset-1 ring-offset-surface' : ''
      } ${className}`}
      style={{ width: size, height: size, fontSize: Math.max(11, Math.round(size * 0.4)) }}
      role="img"
      aria-label={name ? `Avatar of ${name}` : 'Avatar'}
      {...props}
    >
      {initials}
    </span>
  );
}