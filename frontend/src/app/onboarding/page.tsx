
"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000/api/v1";

export default function OnboardingPage() {
  const router = useRouter();

  const [domain, setDomain] = useState("Computer Vision");
  const [description, setDescription] = useState("");
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [digestTime, setDigestTime] = useState("08:00");

  const [interests, setInterests] = useState<string[]>([]);
  const [excluded, setExcluded] = useState<string[]>([]);

  const [interestInput, setInterestInput] = useState("");
  const [excludedInput, setExcludedInput] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("zealwithin_token")
      : null;

  function addKeyword(
    value: string,
    type: "interest" | "excluded"
  ) {
    const keyword = value.trim();

    if (!keyword) return;

    if (type === "interest") {
      if (!interests.some((item) => item.toLowerCase() === keyword.toLowerCase())) {
        setInterests([...interests, keyword]);
      }
      setInterestInput("");
    } else {
      if (!excluded.some((item) => item.toLowerCase() === keyword.toLowerCase())) {
        setExcluded([...excluded, keyword]);
      }
      setExcludedInput("");
    }
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (!token) {
      router.push("/");
      return;
    }

    if (interests.length === 0) {
      setError("Please add at least one research interest.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const profileResponse = await fetch(`${API_URL}/profile`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          domain,
          description,
          timezone,
          digest_time: digestTime,
        }),
      });

      const profileData = await profileResponse.json();

      if (!profileResponse.ok) {
        throw new Error(
          profileData.detail ?? "Could not create research profile."
        );
      }

      for (const keyword of interests) {
        const response = await fetch(`${API_URL}/profile/keywords`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            keyword,
            is_excluded: false,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to save research interests.");
        }
      }

      for (const keyword of excluded) {
        const response = await fetch(`${API_URL}/profile/keywords`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            keyword,
            is_excluded: true,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to save excluded keywords.");
        }
      }

      router.push("/dashboard");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f7f8fc] px-5 py-12">
      <div className="max-w-3xl mx-auto">

        <div className="mb-10">
          <p className="text-blue-600 font-semibold text-sm mb-2">
            RESEARCHIFY · GETTING STARTED
          </p>

          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Let&aposs personalize your research.
          </h1>

          <p className="text-gray-500">
            Tell us what you&aposre researching. We&aposll find papers
            that match your interests.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-3xl shadow-sm border border-gray-100 p-7 md:p-10 space-y-8"
        >
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2">
              Research domain
            </label>

            <input
              required
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="e.g. Computer Vision"
              className="w-full rounded-xl border border-gray-200 p-3.5 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2">
              Research description
            </label>

            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Describe your research goals and interests..."
              className="w-full rounded-xl border border-gray-200 p-3.5 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-3">
              Research interests
            </label>

            <div className="flex gap-2">
              <input
                value={interestInput}
                onChange={(e) => setInterestInput(e.target.value)}
                placeholder="e.g. Object Detection"
                className="flex-1 min-w-0 rounded-xl border border-gray-200 p-3 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
              />

              <button
                type="button"
                onClick={() => addKeyword(interestInput, "interest")}
                className="bg-blue-600 text-white rounded-xl px-5 font-semibold hover:bg-blue-700"
              >
                Add
              </button>
            </div>

            <div className="flex flex-wrap gap-2 mt-4">
              {interests.map((keyword) => (
                <button
                  type="button"
                  key={keyword}
                  onClick={() =>
                    setInterests(interests.filter((item) => item !== keyword))
                  }
                  className="bg-blue-50 text-blue-700 px-3 py-2 rounded-lg text-sm"
                >
                  {keyword} ×
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-3">
              Excluded keywords
            </label>

            <div className="flex gap-2">
              <input
                value={excludedInput}
                onChange={(e) => setExcludedInput(e.target.value)}
                placeholder="e.g. Medical Imaging"
                className="flex-1 min-w-0 rounded-xl border border-gray-200 p-3 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
              />

              <button
                type="button"
                onClick={() => addKeyword(excludedInput, "excluded")}
                className="bg-gray-800 text-white rounded-xl px-5 font-semibold hover:bg-gray-900"
              >
                Add
              </button>
            </div>

            <div className="flex flex-wrap gap-2 mt-4">
              {excluded.map((keyword) => (
                <button
                  type="button"
                  key={keyword}
                  onClick={() =>
                    setExcluded(excluded.filter((item) => item !== keyword))
                  }
                  className="bg-red-50 text-red-700 px-3 py-2 rounded-lg text-sm"
                >
                  {keyword} ×
                </button>
              ))}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">
                Timezone
              </label>

              <input
                required
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full rounded-xl border border-gray-200 p-3 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">
                Preferred digest time
              </label>

              <input
                type="time"
                required
                value={digestTime}
                onChange={(e) => setDigestTime(e.target.value)}
                className="w-full rounded-xl border border-gray-200 p-3 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-50 text-red-700 rounded-xl p-4 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold py-4 rounded-xl transition"
          >
            {loading ? "Setting up your research profile..." : "Complete setup →"}
          </button>
        </form>

        <p className="text-center text-xs text-gray-400 mt-6">
          Your research journey starts here.
        </p>
      </div>
    </main>
  );
}
