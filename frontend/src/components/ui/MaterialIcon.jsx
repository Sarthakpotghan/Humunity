export default function MaterialIcon({ 
  name, 
  size = 24, 
  className = "", 
  fill = 0, 
  weight = 400,
  grade = 0,
  opticalSize = 24,
  ...props 
}) {
  return (
    <span
      className={`material-symbols-outlined ${className}`}
      style={{
        fontSize: `${size}px`,
        fontVariationSettings: `'FILL' ${fill}, 'wght' ${weight}, 'GRAD' ${grade}, 'opsz' ${opticalSize}`,
      }}
      {...props}
    >
      {name}
    </span>
  );
}