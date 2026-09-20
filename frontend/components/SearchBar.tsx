"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { cn } from "@/lib/utils";

export function SearchBar({
  initialValue = "",
  onSubmitNavigate = true,
  autoFocus = false,
  className,
  placeholder = "Search movies by title…",
}: {
  initialValue?: string;
  /** If true (default), submitting navigates to /search?q=… — used in the navbar. */
  onSubmitNavigate?: boolean;
  autoFocus?: boolean;
  className?: string;
  placeholder?: string;
}) {
  const [value, setValue] = useState(initialValue);
  const router = useRouter();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!value.trim()) return;
    if (onSubmitNavigate) {
      router.push(`/search?q=${encodeURIComponent(value.trim())}`);
    }
  }

  return (
    <form onSubmit={handleSubmit} role="search" className={cn("relative", className)}>
      <label htmlFor="global-search" className="sr-only">
        Search movies
      </label>
      <svg
        aria-hidden="true"
        viewBox="0 0 20 20"
        className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint"
        fill="none"
      >
        <circle cx="9" cy="9" r="6" stroke="currentColor" strokeWidth="1.5" />
        <path d="M14 14l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
      <input
        id="global-search"
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className="w-full rounded-lg border border-base-border bg-base-surface py-2 pl-9 pr-3 text-sm text-ink placeholder:text-ink-faint focus:border-accent-soft focus:outline-none"
      />
    </form>
  );
}
