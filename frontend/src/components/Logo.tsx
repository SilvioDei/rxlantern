// Original RxLantern lantern logo (SVG) with a soft amber glow.
export function Logo({ size = 44, label }: { size?: number; label?: string }) {
  return (
    <svg className="logo" width={size} height={size} viewBox="0 0 64 64" role={label ? "img" : undefined}
      aria-label={label} aria-hidden={label ? undefined : true}>
      <defs>
        <radialGradient id="lg-glow" cx="50%" cy="52%" r="50%">
          <stop offset="0%" stopColor="#ffd98a" stopOpacity="0.95" />
          <stop offset="60%" stopColor="#f4b740" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#f4b740" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="lg-glass" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#fff4d6" />
          <stop offset="100%" stopColor="#fbd88a" />
        </linearGradient>
      </defs>
      <circle className="logo-glow" cx="32" cy="33" r="27" fill="url(#lg-glow)" />
      <path d="M26 9.5a6 6 0 0 1 12 0" fill="none" stroke="#f4b740" strokeWidth="2.6" strokeLinecap="round" />
      <rect x="22" y="11" width="20" height="5" rx="2.5" fill="#f4b740" />
      <path d="M21 18h22l-2.6 25.5H23.6z" fill="url(#lg-glass)" stroke="#f4b740" strokeWidth="2.4" strokeLinejoin="round" />
      <path d="M32 22v17M27 30.5h10" stroke="#0e5c63" strokeWidth="3" strokeLinecap="round" />
      <rect x="21" y="44.5" width="22" height="5.5" rx="2.5" fill="#f4b740" />
      <path d="M27 50v3.5h10V50" fill="none" stroke="#f4b740" strokeWidth="2.4" strokeLinejoin="round" />
    </svg>
  );
}
