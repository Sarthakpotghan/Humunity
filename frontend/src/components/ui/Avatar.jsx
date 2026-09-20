export default function Avatar({ 
  src, 
  alt = "", 
  size = 36, 
  className = "",
  ring = true,
  ...props 
}) {
  return (
    <img
      src={src}
      alt={alt}
      className={`w-[${size}px] h-[${size}px] rounded-full object-cover ${ring ? 'ring-2 ring-primary-container/20 shadow-sm' : ''} ${className}`}
      {...props}
    />
  );
}