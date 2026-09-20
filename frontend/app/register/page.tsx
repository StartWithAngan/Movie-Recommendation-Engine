"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { authApi } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { useAuth } from "@/lib/auth-context";

const MIN_PASSWORD_LENGTH = 8; // matches backend/app/schemas/schemas.py UserRegister

export default function RegisterPage() {
  const router = useRouter();
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();

  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated) router.replace("/discover");
  }, [authLoading, isAuthenticated, router]);

  function validate(): string | null {
    if (!displayName.trim()) return "Enter a display name.";
    if (!email.trim() || !email.includes("@")) return "Enter a valid email address.";
    if (password.length < MIN_PASSWORD_LENGTH) return `Password must be at least ${MIN_PASSWORD_LENGTH} characters.`;
    return null;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const validationError = validate();
    setError(validationError);
    if (validationError) return;

    setSubmitting(true);
    try {
      const { access_token } = await authApi.register(email.trim(), password, displayName.trim());
      await login(access_token);
      router.push("/discover");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm animate-fade-in py-10">
      <p className="text-center text-xs font-semibold uppercase tracking-[0.2em] text-accent-soft">CineLens</p>
      <h1 className="mt-3 text-center text-2xl font-bold text-ink">Create your account</h1>
      <p className="mt-1.5 text-center text-sm text-ink-muted">Your ratings power your personalized recommendations.</p>

      <form onSubmit={handleSubmit} className="glass mt-8 space-y-4 rounded-2xl p-6" noValidate>
        <div>
          <label htmlFor="display_name" className="mb-1.5 block text-sm font-medium text-ink">
            Display name
          </label>
          <input
            id="display_name"
            type="text"
            autoComplete="name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            maxLength={80}
            required
            className="w-full rounded-lg border border-base-border bg-base-surface px-3 py-2 text-sm text-ink focus:border-accent-soft focus:outline-none"
          />
        </div>

        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-ink">
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-lg border border-base-border bg-base-surface px-3 py-2 text-sm text-ink focus:border-accent-soft focus:outline-none"
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-ink">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={MIN_PASSWORD_LENGTH}
              required
              className="w-full rounded-lg border border-base-border bg-base-surface px-3 py-2 pr-16 text-sm text-ink focus:border-accent-soft focus:outline-none"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-medium text-ink-muted hover:text-ink"
              aria-pressed={showPassword}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
          <p className="mt-1 text-xs text-ink-faint">At least {MIN_PASSWORD_LENGTH} characters.</p>
        </div>

        {error && (
          <p role="alert" className="rounded-lg border border-red-500/20 bg-red-500/[0.06] px-3 py-2 text-sm text-red-300">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="accent-gradient-bg w-full rounded-lg py-2.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-60"
        >
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="mt-5 text-center text-sm text-ink-muted">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-accent-soft hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
