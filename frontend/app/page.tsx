"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { SearchBar } from "@/components/SearchBar";

const FEATURES = [
  {
    title: "Personalized recommendations",
    description: "Every rating you give sharpens what we suggest next — the more you rate, the better it gets.",
  },
  {
    title: "Content-based similarity",
    description: "Find movies that share the DNA of ones you already love — genre, tone, and theme.",
  },
  {
    title: "Collaborative filtering",
    description: "See what people with taste like yours are watching, not just what's broadly popular.",
  },
  {
    title: "Cold-start recommendations",
    description: "New here? You'll still get thoughtful suggestions from the moment you rate your first movie.",
  },
  {
    title: "Explainable recommendations",
    description: "Every suggestion tells you why it's there — no black-box scores, just plain language.",
  },
];

export default function LandingPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace("/discover");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || isAuthenticated) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="skeleton h-8 w-8 rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-24 pb-16">
      <section className="animate-fade-in pt-8 text-center sm:pt-16">
        <p className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-accent-soft">
          Machine learning × cinema
        </p>
        <h1 className="mx-auto max-w-3xl text-4xl font-extrabold leading-[1.05] tracking-tight text-ink sm:text-6xl">
          Movies chosen for <span className="accent-gradient-text">your</span> taste
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-base text-ink-muted sm:text-lg">
          CineLens blends content similarity, collaborative filtering, and a hybrid ranker to turn a handful of
          ratings into recommendations that actually fit you.
        </p>

        <div className="mx-auto mt-8 max-w-md">
          <SearchBar placeholder="Try searching for a movie…" />
        </div>

        <div className="mt-6 flex items-center justify-center gap-3">
          <Link
            href="/register"
            className="accent-gradient-bg rounded-lg px-5 py-2.5 text-sm font-semibold text-white shadow-glow transition hover:opacity-90"
          >
            Create your account
          </Link>
          <Link
            href="/login"
            className="rounded-lg border border-base-border px-5 py-2.5 text-sm font-medium text-ink transition hover:border-base-borderStrong"
          >
            Sign in
          </Link>
        </div>
      </section>

      <section aria-labelledby="features-heading">
        <h2 id="features-heading" className="sr-only">
          Features
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {FEATURES.map((feature) => (
            <div key={feature.title} className="glass animate-fade-in rounded-2xl p-5">
              <h3 className="text-sm font-semibold text-ink">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-ink-muted">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
