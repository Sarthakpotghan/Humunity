import MaterialIcon from './MaterialIcon';

export default function Logo({ size = 'md', variant = 'full', className = '' }) {
  const dimensions = {
    sm: { icon: 26, text: 'text-[18px]', gap: 'gap-2' },
    md: { icon: 30, text: 'text-[22px]', gap: 'gap-2.5' },
    lg: { icon: 38, text: 'text-[30px]', gap: 'gap-3' },
    xl: { icon: 48, text: 'text-[38px]', gap: 'gap-3.5' },
  }[size] || { icon: 30, text: 'text-[22px]', gap: 'gap-2.5' };

  return (
    <span
      className={`inline-flex items-center ${dimensions.gap} ${className}`}
      aria-label="Humunity"
    >
      <span
        className="bg-gradient-primary rounded-full flex items-center justify-center text-on-primary shadow-card shrink-0"
        style={{ width: dimensions.icon, height: dimensions.icon }}
      >
        <MaterialIcon name="volunteer_activism" size={Math.round(dimensions.icon * 0.62)} />
      </span>
      {variant === 'full' && (
        <span className={`${dimensions.text} font-headline-md font-extrabold text-primary-container tracking-tight leading-none whitespace-nowrap`}>
          Humunity
        </span>
      )}
    </span>
  );
}