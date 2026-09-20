"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { SearchBar } from "./SearchBar";
import { cn } from "@/lib/utils";

const AUTHED_LINKS = [
  { href: "/discover", label: "Discover" },
  { href: "/search", label: "Search" },
  { href: "/ratings", label: "My Ratings" },
  { href: "/watchlist", label: "Watchlist" },
  { href: "/profile", label: "Profile" },
];

export function Navbar() {
  const { isAuthenticated, isLoading, user, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [drawerOpen, setDrawerOpen] = useState(false);

  function handleLogout() {
    logout();
    setDrawerOpen(false);
    router.push("/");
  }

  return (
    <header className="sticky top-0 z-30 border-b border-base-border/80 bg-base-bg/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6">
        <Link href="/" className="shrink-0 text-lg font-extrabold tracking-tight text-ink">
          Cine<span className="accent-gradient-text">Lens</span>
        </Link>

        {isAuthenticated && (
          <nav className="hidden items-center gap-1 md:flex" aria-label="Main navigation">
            {AUTHED_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-lg px-3 py-1.5 text-sm transition",
                  pathname === link.href ? "bg-white/[0.06] text-ink" : "text-ink-muted hover:text-ink"
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        )}

        {isAuthenticated && (
          <div className="ml-auto hidden max-w-xs flex-1 md:block">
            <SearchBar />
          </div>
        )}

        <div className="ml-auto flex items-center gap-3 md:ml-4">
          {!isLoading && !isAuthenticated && (
            <div className="hidden items-center gap-2 sm:flex">
              <Link href="/login" className="rounded-lg px-3 py-1.5 text-sm text-ink-muted hover:text-ink">
                Sign in
              </Link>
              <Link
                href="/register"
                className="accent-gradient-bg rounded-lg px-4 py-1.5 text-sm font-medium text-white transition hover:opacity-90"
              >
                Get started
              </Link>
            </div>
          )}

          {isAuthenticated && (
            <div className="hidden items-center gap-3 md:flex">
              <span className="text-sm text-ink-muted">{user?.display_name}</span>
              <button
                onClick={handleLogout}
                className="rounded-lg border border-base-border px-3 py-1.5 text-sm text-ink-muted transition hover:border-base-borderStrong hover:text-ink"
              >
                Log out
              </button>
            </div>
          )}

          <button
            onClick={() => setDrawerOpen(true)}
            className="rounded-lg p-2 text-ink-muted hover:text-ink md:hidden"
            aria-label="Open menu"
            aria-expanded={drawerOpen}
          >
            <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
              <path d="M4 7h16M4 12h16M4 17h16" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setDrawerOpen(false)} aria-hidden="true" />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Navigation menu"
            className="absolute right-0 top-0 h-full w-72 max-w-[85vw] border-l border-base-border bg-base-surface p-5"
          >
            <div className="mb-6 flex items-center justify-between">
              <span className="text-base font-semibold text-ink">Menu</span>
              <button onClick={() => setDrawerOpen(false)} aria-label="Close menu" className="p-1 text-ink-muted hover:text-ink">
                <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="M6 6l12 12M18 6L6 18" strokeLinecap="round" />
                </svg>
              </button>
            </div>

            <div className="mb-5">
              <SearchBar />
            </div>

            {isAuthenticated ? (
              <>
                <nav className="flex flex-col gap-1" aria-label="Mobile navigation">
                  {AUTHED_LINKS.map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      onClick={() => setDrawerOpen(false)}
                      className={cn(
                        "rounded-lg px-3 py-2 text-sm",
                        pathname === link.href ? "bg-white/[0.06] text-ink" : "text-ink-muted hover:text-ink"
                      )}
                    >
                      {link.label}
                    </Link>
                  ))}
                </nav>
                <div className="mt-6 border-t border-base-border pt-4">
                  <p className="mb-2 text-sm text-ink-muted">{user?.display_name}</p>
                  <button
                    onClick={handleLogout}
                    className="w-full rounded-lg border border-base-border px-3 py-2 text-left text-sm text-ink-muted hover:text-ink"
                  >
                    Log out
                  </button>
                </div>
              </>
            ) : (
              <div className="flex flex-col gap-2">
                <Link
                  href="/login"
                  onClick={() => setDrawerOpen(false)}
                  className="rounded-lg border border-base-border px-3 py-2 text-center text-sm text-ink"
                >
                  Sign in
                </Link>
                <Link
                  href="/register"
                  onClick={() => setDrawerOpen(false)}
                  className="accent-gradient-bg rounded-lg px-3 py-2 text-center text-sm font-medium text-white"
                >
                  Get started
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
