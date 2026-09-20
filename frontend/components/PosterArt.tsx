/**
 * The backend's MovieOut/Recommendation/WatchlistOut schemas carry no poster
 * or image URL (see backend/app/schemas/schemas.py) — there is no poster
 * provider wired up yet. Rather than inventing a URL or hardcoding a static
 * placeholder image, this derives a distinctive-but-deterministic gradient
 * per movie (so the same movie always looks the same) and shows initials.
 *
 * To add real posters later: give this component an optional `posterUrl`
 * prop, render an <img> when present, and fall back to this component
 * otherwise — no other call site needs to change.
 */

const GRADIENTS = [
  "from-indigo-600/70 via-purple-600/50 to-slate-900",
  "from-rose-600/60 via-fuchsia-700/45 to-slate-900",
  "from-amber-600/55 via-orange-700/40 to-slate-900",
  "from-emerald-600/55 via-teal-700/40 to-slate-900",
  "from-sky-600/60 via-blue-700/45 to-slate-900",
  "from-violet-600/60 via-indigo-800/45 to-slate-900",
];

function hashTitle(title: string): number {
  let hash = 0;
  for (let i = 0; i < title.length; i++) {
    hash = (hash * 31 + title.charCodeAt(i)) >>> 0;
  }
  return hash;
}

function initials(title: string): string {
  const words = title.replace(/\(.*?\)/g, "").trim().split(/\s+/).filter(Boolean);
  const letters = words.slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "");
  return letters.join("") || "?";
}

export function PosterArt({ title, className }: { title: string; className?: string }) {
  const gradient = GRADIENTS[hashTitle(title) % GRADIENTS.length];
  return (
    <div
      className={`relative flex items-center justify-center overflow-hidden rounded-xl bg-gradient-to-br ${gradient} ${className ?? ""}`}
      aria-hidden="true"
    >
      <span className="text-2xl font-bold tracking-tight text-white/85 drop-shadow-sm">{initials(title)}</span>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.15),transparent_60%)]" />
    </div>
  );
}
