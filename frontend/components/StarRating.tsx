"use client";

import { useId, useState } from "react";
import { cn } from "@/lib/utils";

const STAR_VALUES = [1, 2, 3, 4, 5];

function StarIcon({ fill }: { fill: number }) {
  // fill: 0, 0.5, or 1 — how much of this star is filled
  const gradientId = useId();
  return (
    <svg viewBox="0 0 24 24" className="h-full w-full" aria-hidden="true">
      <defs>
        <linearGradient id={gradientId}>
          <stop offset={`${fill * 100}%`} stopColor="currentColor" />
          <stop offset={`${fill * 100}%`} stopColor="transparent" />
        </linearGradient>
      </defs>
      <path
        d="M12 2.5l2.9 6.16 6.6.72-4.9 4.6 1.28 6.52L12 17.6l-5.88 3.3L7.4 14.4l-4.9-4.6 6.6-.72L12 2.5z"
        fill={`url(#${gradientId})`}
        stroke="currentColor"
        strokeWidth="1.2"
        className="text-amber-400"
      />
    </svg>
  );
}

export function StarRating({
  value,
  onChange,
  size = "md",
  readOnly = false,
  label = "Rating",
}: {
  value: number;
  onChange?: (rating: number) => void;
  size?: "sm" | "md" | "lg";
  readOnly?: boolean;
  label?: string;
}) {
  const [hoverValue, setHoverValue] = useState<number | null>(null);
  const displayValue = hoverValue ?? value;
  const dimension = size === "sm" ? "h-4 w-4" : size === "lg" ? "h-8 w-8" : "h-6 w-6";

  function fillFor(star: number): number {
    if (displayValue >= star) return 1;
    if (displayValue >= star - 0.5) return 0.5;
    return 0;
  }

  if (readOnly || !onChange) {
    return (
      <div className="flex items-center gap-2" role="img" aria-label={`${label}: ${value} out of 5 stars`}>
        <div className="flex gap-0.5">
          {STAR_VALUES.map((star) => (
            <div key={star} className={dimension}>
              <StarIcon fill={fillFor(star)} />
            </div>
          ))}
        </div>
        <span className="text-sm text-ink-muted">{value.toFixed(1)}</span>
      </div>
    );
  }

  return (
    <div
      className="inline-flex items-center gap-2"
      role="radiogroup"
      aria-label={label}
      onMouseLeave={() => setHoverValue(null)}
    >
      <div className="flex gap-0.5">
        {STAR_VALUES.map((star) => (
          <div key={star} className={cn("relative", dimension)}>
            <div className={cn("pointer-events-none", dimension)}>
              <StarIcon fill={fillFor(star)} />
            </div>
            {/* Two half-width buttons stacked over each star icon for 0.5-step precision */}
            <button
              type="button"
              role="radio"
              aria-checked={value === star - 0.5}
              aria-label={`Rate ${star - 0.5} out of 5 stars`}
              className="absolute inset-y-0 left-0 w-1/2 cursor-pointer"
              onMouseEnter={() => setHoverValue(star - 0.5)}
              onFocus={() => setHoverValue(star - 0.5)}
              onBlur={() => setHoverValue(null)}
              onClick={() => onChange(star - 0.5)}
            />
            <button
              type="button"
              role="radio"
              aria-checked={value === star}
              aria-label={`Rate ${star} out of 5 stars`}
              className="absolute inset-y-0 right-0 w-1/2 cursor-pointer"
              onMouseEnter={() => setHoverValue(star)}
              onFocus={() => setHoverValue(star)}
              onBlur={() => setHoverValue(null)}
              onClick={() => onChange(star)}
            />
          </div>
        ))}
      </div>
      <span className="min-w-[2.5rem] text-sm text-ink-muted" aria-live="polite">
        {displayValue > 0 ? displayValue.toFixed(1) : "Rate"}
      </span>
    </div>
  );
}
