
"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000/api/v1";

export default function Home() {
  const [isRegister, setIsRegister] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    setLoading(true);
    setError("");
    setMessage("");

    try {
      if (isRegister) {
        const registerResponse = await fetch(
          `${API_URL}/auth/register`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              full_name: fullName,
              email,
              password,
            }),
          }
        );

        const registerData = await registerResponse.json();

        if (!registerResponse.ok) {
          throw new Error(
            registerData.detail ?? "Registration failed."
          );
        }
      }

      const loginResponse = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const loginData = await loginResponse.json();

      if (!loginResponse.ok) {
        throw new Error(loginData.detail ?? "Login failed.");
      }

        const token = loginData.access_token;

        localStorage.setItem("zealwithin_token", token);

        // Check whether the user already has a research profile.
        const profileResponse = await fetch(`${API_URL}/profile`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (profileResponse.ok) {
          router.replace("/dashboard");
        } else if (profileResponse.status === 404) {
          router.replace("/onboarding");
        } else {
          throw new Error("Could not verify your research profile.");
        }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f7f8fc] flex items-center justify-center p-5">
      <div className="w-full max-w-5xl grid md:grid-cols-2 bg-white rounded-3xl shadow-xl overflow-hidden">

        {/* Left panel */}
        <section className="bg-[#172554] text-white p-10 md:p-14 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3 mb-16">
              <div className="w-11 h-11 rounded-xl bg-blue-500 flex items-center justify-center text-2xl font-bold">
                R
              </div>
              <span className="text-2xl font-bold tracking-tight">
                ZealWithin
              </span>
            </div>

            <p className="text-blue-300 text-sm font-semibold uppercase tracking-widest mb-4">
              Your research companion
            </p>

            <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6">
              Keep the researcher in you alive.
            </h1>

            <p className="text-blue-100 leading-7 text-base">
              Discover meaningful research, explore new ideas,
              and stay ahead in your research journey.
            </p>
          </div>

          <div className="mt-16 space-y-5">
            {[
              ["01", "Discover the latest academic papers"],
              ["02", "Get recommendations tailored to you"],
              ["03", "Never miss important research"],
            ].map(([number, text]) => (
              <div key={number} className="flex items-center gap-4">
                <span className="text-blue-300 font-bold">
                  {number}
                </span>
                <span className="text-sm text-blue-100">
                  {text}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Right panel */}
        <section className="p-8 md:p-14 flex flex-col justify-center">
          <p className="text-sm text-blue-600 font-semibold mb-3">
            WELCOME TO ZealWithin
          </p>

          <h2 className="text-3xl font-bold text-gray-900 mb-3">
            {isRegister ? "Create your account" : "Welcome back"}
          </h2>

          <p className="text-gray-500 mb-8">
            {isRegister
              ? "Start your personalized research journey."
              : "Sign in to continue your research journey."}
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            {isRegister && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full name
                </label>
                <input
                  type="text"
                  required
                  minLength={2}
                  maxLength={150}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                  className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                maxLength={128}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {error && (
              <div className="rounded-xl bg-red-50 text-red-700 p-3 text-sm">
                {error}
              </div>
            )}

            {message && (
              <div className="rounded-xl bg-green-50 text-green-700 p-3 text-sm">
                {message}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold py-3.5 transition"
            >
              {loading
                ? "Please wait..."
                : isRegister
                  ? "Create account"
                  : "Sign in"}
            </button>
          </form>

          <div className="mt-7 text-center text-sm text-gray-500">
            {isRegister
              ? "Already have an account?"
              : "New to ZealWithin?"}

            <button
              type="button"
              onClick={() => {
                setIsRegister(!isRegister);
                setError("");
                setMessage("");
              }}
              className="ml-2 text-blue-600 font-semibold hover:underline"
            >
              {isRegister ? "Sign in" : "Create an account"}
            </button>
          </div>

          <p className="text-center text-xs text-gray-400 mt-12">
            ZealWithin · Keep the researcher in you alive.
          </p>
        </section>
      </div>
    </main>
  );
}
