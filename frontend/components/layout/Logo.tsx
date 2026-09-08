type LogoProps = { size?: number };

export function Logo({ size = 20 }: LogoProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="1" y="1" width="22" height="22" rx="6" fill="#1f6feb" />
      <path d="M9 9l-3 3 3 3" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M15 9l3 3-3 3" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}