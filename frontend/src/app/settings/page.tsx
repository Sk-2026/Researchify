
"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

type Keyword = {
  id: string;
  keyword: string;
  category: string | null;
  is_excluded: boolean;
};

type Profile = {
  id: string;
  domain: string;
  description: string | null;
  timezone: string;
  digest_time: string;
  keywords: Keyword[];
};

type PaperCandidate = {
  title: string;
  doi: string | null;
  abstract: string | null;
  authors: string[];
  publication_date: string | null;
  venue: string | null;
  suggested_keywords: string[];
};

export default function SettingsPage() {
  const router = useRouter();

  const [profile, setProfile] = useState<Profile | null>(null);
  const [domain, setDomain] = useState("");
  const [description, setDescription] = useState("");
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [digestTime, setDigestTime] = useState("08:00");

  const [newInterest, setNewInterest] = useState("");
  const [newExcluded, setNewExcluded] = useState("");

  const [importQuery, setImportQuery] = useState("");
  const [importing, setImporting] = useState(false);
  const [approvingKeywords, setApprovingKeywords] = useState(false);
  const [candidates, setCandidates] = useState<PaperCandidate[]>([]);
  const [selectedCandidateIndex, setSelectedCandidateIndex] = useState(0);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const getToken = () => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("zealwithin_token");
  };

  const loadProfile = useCallback(async () => {
    const token = getToken();

    if (!token) {
      router.replace("/");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/profile`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        cache: "no-store",
      });

      if (response.status === 401) {
        localStorage.removeItem("zealwithin_token");
        router.replace("/");
        return;
      }

      if (!response.ok) {
        throw new Error("Could not load your research profile.");
      }

      const data: Profile = await response.json();

      setProfile(data);
      setDomain(data.domain ?? "");
      setDescription(data.description ?? "");
      setTimezone(data.timezone ?? "Asia/Kolkata");
      setDigestTime(data.digest_time ?? "08:00");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const token = getToken();
    if (!token) {
      router.replace("/");
      return;
    }

    try {
      setSaving(true);
      setMessage("");
      setError("");

      const response = await fetch(`${API_URL}/profile`, {
        method: "PUT",
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

      if (response.status === 401) {
        localStorage.removeItem("zealwithin_token");
        router.replace("/");
        return;
      }

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail ?? "Could not save your profile.");
      }

      setMessage("Research profile updated successfully.");
      await loadProfile();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not save your profile."
      );
    } finally {
      setSaving(false);
    }
  }

  async function addKeyword(isExcluded: boolean) {
    const keyword = isExcluded ? newExcluded.trim() : newInterest.trim();

    if (!keyword) return;

    const token = getToken();
    if (!token) {
      router.replace("/");
      return;
    }

    try {
      setError("");
      setMessage("");

      const response = await fetch(`${API_URL}/profile/keywords`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          keyword,
          category: null,
          is_excluded: isExcluded,
        }),
      });

      if (response.status === 401) {
        localStorage.removeItem("zealwithin_token");
        router.replace("/");
        return;
      }

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail ?? "Could not add this keyword.");
      }

      if (isExcluded) {
        setNewExcluded("");
      } else {
        setNewInterest("");
      }

      await loadProfile();
      setMessage("Keyword added successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not add keyword."
      );
    }
  }

  async function deleteKeyword(keywordId: string) {
    const token = getToken();
    if (!token) {
      router.replace("/");
      return;
    }

    try {
      setError("");
      setMessage("");

      const response = await fetch(
        `${API_URL}/profile/keywords/${keywordId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 401) {
        localStorage.removeItem("zealwithin_token");
        router.replace("/");
        return;
      }

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail ?? "Could not delete this keyword.");
      }

      await loadProfile();
      setMessage("Keyword removed successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not delete keyword."
      );
    }
  }

  async function lookupPaper(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const query = importQuery.trim();

    if (!query) {
      setError("Please enter a paper title or DOI.");
      return;
    }

    const token = getToken();

    if (!token) {
      router.replace("/");
      return;
    }

    try {
      setImporting(true);
      setError("");
      setMessage("");
      setCandidates([]);
      setSelectedKeywords([]);
      setSelectedCandidateIndex(0);

      const response = await fetch(
        `${API_URL}/profile/suggest-keyword`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query }),
        }
      );

      if (response.status === 401) {
        localStorage.removeItem("zealwithin_token");
        router.replace("/");
        return;
      }

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail ?? "Could not retrieve paper information."
        );
      }

      const results: PaperCandidate[] = data?.candidates ?? [];

      if (results.length === 0) {
        throw new Error("No matching papers were found.");
      }

      setCandidates(results);
      setSelectedCandidateIndex(0);
      setSelectedKeywords(results[0].suggested_keywords ?? []);

      setMessage(
        `${results.length} matching paper${results.length === 1 ? "" : "s"} found. Review the details and suggested keywords.`
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not retrieve paper information."
      );
    } finally {
      setImporting(false);
    }
  }

  function changeCandidate(index: number) {
    setSelectedCandidateIndex(index);

    const candidate = candidates[index];

    setSelectedKeywords(candidate?.suggested_keywords ?? []);
  }

  function toggleSuggestedKeyword(keyword: string) {
    setSelectedKeywords((current) =>
      current.includes(keyword)
        ? current.filter((item) => item !== keyword)
        : [...current, keyword]
    );
  }

  async function approveSuggestedKeywords() {
    if (selectedKeywords.length === 0) {
      setError("Please select at least one keyword to add.");
      return;
    }

    const token = getToken();

    if (!token) {
      router.replace("/");
      return;
    }

    try {
      setApprovingKeywords(true);
      setError("");
      setMessage("");

      let addedCount = 0;
      let existingCount = 0;
      let failedCount = 0;

      for (const keyword of selectedKeywords) {
        const response = await fetch(`${API_URL}/profile/keywords`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            keyword,
            category: null,
            is_excluded: false,
          }),
        });

        if (response.status === 401) {
          localStorage.removeItem("zealwithin_token");
          router.replace("/");
          return;
        }

        if (response.ok) {
          addedCount++;
        } else {
          const data = await response.json().catch(() => null);
          const detail = String(data?.detail ?? "").toLowerCase();

          if (
            response.status === 409 ||
            detail.includes("already exists") ||
            detail.includes("duplicate")
          ) {
            existingCount++;
          } else {
            failedCount++;
          }
        }
      }

      await loadProfile();

      if (failedCount > 0) {
        setMessage(
          `${addedCount} keyword(s) added, ${existingCount} already existed, and ${failedCount} could not be added.`
        );
      } else {
        setMessage(
          `${addedCount} keyword(s) added successfully. ${existingCount} already existed.`
        );
      }

      setSelectedKeywords([]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not add the selected keywords."
      );
    } finally {
      setApprovingKeywords(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-50 p-8 text-slate-700">
        Loading your research settings...
      </main>
    );
  }

  if (!profile) {
    return (
      <main className="min-h-screen bg-slate-50 p-8">
        <p className="text-red-600">
          {error || "Your research profile could not be loaded."}
        </p>
        <button
          onClick={() => void loadProfile()}
          className="mt-4 rounded-lg bg-blue-700 px-4 py-2 text-white"
        >
          Try again
        </button>
      </main>
    );
  }

  const interests = profile.keywords.filter(
    (keyword) => !keyword.is_excluded
  );

  const excludedKeywords = profile.keywords.filter(
    (keyword) => keyword.is_excluded
  );

  const selectedPaper = candidates[selectedCandidateIndex];

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 text-slate-900 sm:px-8">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">
              ZealWithin
            </p>
            <h1 className="mt-1 text-3xl font-bold">Research Settings</h1>
            <p className="mt-2 text-slate-600">
              Manage your research profile and discovery interests.
            </p>
          </div>

          <button
            onClick={() => router.push("/dashboard")}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-100"
          >
            Back to Dashboard
          </button>
        </header>

        {message && (
          <div className="mb-5 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800">
            {message}
          </div>
        )}

        {error && (
          <div className="mb-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-xl font-semibold">Research Profile</h2>

          <form onSubmit={saveProfile} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium">
                Research Domain
              </label>
              <input
                value={domain}
                onChange={(event) => setDomain(event.target.value)}
                required
                minLength={2}
                maxLength={150}
                className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-600"
                placeholder="e.g. Computer Vision"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Research Description
              </label>
              <textarea
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                rows={4}
                className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-600"
                placeholder="Describe your research goals and interests..."
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Timezone
              </label>
              <input
                value={timezone}
                onChange={(event) => setTimezone(event.target.value)}
                maxLength={100}
                className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-600"
                placeholder="Asia/Kolkata"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Daily Digest Time
              </label>
              <input
                type="time"
                value={digestTime}
                onChange={(event) => setDigestTime(event.target.value)}
                required
                className="rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-600"
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-blue-700 px-5 py-3 font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {saving ? "Saving..." : "Save Profile"}
            </button>
          </form>
        </section>

        {/* Paper Import and Keyword Suggestions */}
        <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-2 text-xl font-semibold">
            Import Research Paper
          </h2>

          <p className="mb-5 text-sm text-slate-600">
            Enter a research paper title or DOI. ZealWithin will retrieve its
            metadata and suggest research keywords for your approval.
          </p>

          <form
            onSubmit={lookupPaper}
            className="flex flex-col gap-3 sm:flex-row"
          >
            <input
              value={importQuery}
              onChange={(event) => setImportQuery(event.target.value)}
              minLength={3}
              maxLength={500}
              required
              className="min-w-0 flex-1 rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-600"
              placeholder="Enter paper title or DOI..."
            />

            <button
              type="submit"
              disabled={importing || importQuery.trim().length < 3}
              className="rounded-lg bg-blue-700 px-5 py-3 font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {importing ? "Searching..." : "Find Paper"}
            </button>
          </form>

          {candidates.length > 0 && (
            <div className="mt-6 border-t border-slate-200 pt-6">
              {candidates.length > 1 && (
                <div className="mb-5">
                  <label className="mb-2 block text-sm font-medium">
                    Select the correct paper
                  </label>

                  <select
                    value={selectedCandidateIndex}
                    onChange={(event) =>
                      changeCandidate(Number(event.target.value))
                    }
                    className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-600"
                  >
                    {candidates.map((candidate, index) => (
                      <option key={`${candidate.title}-${index}`} value={index}>
                        {candidate.title}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {selectedPaper && (
                <div>
                  <h3 className="text-lg font-semibold">
                    {selectedPaper.title}
                  </h3>

                  <div className="mt-2 space-y-1 text-sm text-slate-600">
                    {selectedPaper.authors.length > 0 && (
                      <p>
                        <span className="font-medium">Authors:</span>{" "}
                        {selectedPaper.authors.join(", ")}
                      </p>
                    )}

                    {selectedPaper.publication_date && (
                      <p>
                        <span className="font-medium">Published:</span>{" "}
                        {selectedPaper.publication_date}
                      </p>
                    )}

                    {selectedPaper.venue && (
                      <p>
                        <span className="font-medium">Venue:</span>{" "}
                        {selectedPaper.venue}
                      </p>
                    )}

                    {selectedPaper.doi && (
                      <p className="break-all">
                        <span className="font-medium">DOI:</span>{" "}
                        {selectedPaper.doi}
                      </p>
                    )}
                  </div>

                  {selectedPaper.abstract && (
                    <div className="mt-4">
                      <h4 className="mb-2 text-sm font-semibold">Abstract</h4>
                      <p className="whitespace-pre-line text-sm leading-6 text-slate-600">
                        {selectedPaper.abstract}
                      </p>
                    </div>
                  )}

                  <div className="mt-6">
                    <h4 className="mb-2 text-base font-semibold">
                      Suggested Research Keywords
                    </h4>

                    <p className="mb-4 text-sm text-slate-600">
                      Select the keywords you want to add to your research
                      interests. Nothing is saved until you approve your
                      selection.
                    </p>

                    {selectedPaper.suggested_keywords.length === 0 ? (
                      <p className="rounded-lg bg-amber-50 p-4 text-sm text-amber-800">
                        OpenAlex did not provide keywords for this paper.
                        There are no suggestions to approve.
                      </p>
                    ) : (
                      <div className="flex flex-wrap gap-3">
                        {selectedPaper.suggested_keywords.map((keyword) => (
                          <label
                            key={keyword}
                            className={`inline-flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-sm transition ${
                              selectedKeywords.includes(keyword)
                                ? "border-blue-500 bg-blue-50 text-blue-800"
                                : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={selectedKeywords.includes(keyword)}
                              onChange={() =>
                                toggleSuggestedKeyword(keyword)
                              }
                              className="h-4 w-4 accent-blue-700"
                            />
                            {keyword}
                          </label>
                        ))}
                      </div>
                    )}

                    <div className="mt-5 flex flex-wrap items-center gap-3">
                      <button
                        type="button"
                        onClick={() => void approveSuggestedKeywords()}
                        disabled={
                          approvingKeywords || selectedKeywords.length === 0
                        }
                        className="rounded-lg bg-blue-700 px-5 py-3 font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {approvingKeywords
                          ? "Adding Keywords..."
                          : `Add Selected Keywords (${selectedKeywords.length})`}
                      </button>

                      <button
                        type="button"
                        onClick={() => {
                          setCandidates([]);
                          setSelectedKeywords([]);
                          setImportQuery("");
                          setMessage("");
                          setError("");
                        }}
                        className="rounded-lg border border-slate-300 px-5 py-3 text-sm font-medium hover:bg-slate-100"
                      >
                        Clear Results
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-2 text-xl font-semibold">Research Interests</h2>
          <p className="mb-5 text-sm text-slate-600">
            Add topics you want ZealWithin to use when discovering papers.
          </p>

          <div className="mb-5 flex flex-col gap-3 sm:flex-row">
            <input
              value={newInterest}
              onChange={(event) => setNewInterest(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  void addKeyword(false);
                }
              }}
              className="min-w-0 flex-1 rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-600"
              placeholder="e.g. Object Detection"
            />
            <button
              type="button"
              onClick={() => void addKeyword(false)}
              disabled={newInterest.trim().length < 2}
              className="rounded-lg bg-blue-700 px-5 py-3 font-medium text-white hover:bg-blue-800 disabled:opacity-50"
            >
              Add Interest
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {interests.length === 0 && (
              <p className="text-sm text-slate-500">
                No research interests added yet.
              </p>
            )}

            {interests.map((keyword) => (
              <span
                key={keyword.id}
                className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-2 text-sm text-blue-800"
              >
                {keyword.keyword}
                <button
                  type="button"
                  onClick={() => void deleteKeyword(keyword.id)}
                  aria-label={`Remove ${keyword.keyword}`}
                  className="font-bold text-blue-700 hover:text-red-600"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-2 text-xl font-semibold">Excluded Keywords</h2>
          <p className="mb-5 text-sm text-slate-600">
            Add topics you want to exclude from your recommendations.
          </p>

          <div className="mb-5 flex flex-col gap-3 sm:flex-row">
            <input
              value={newExcluded}
              onChange={(event) => setNewExcluded(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  void addKeyword(true);
                }
              }}
              className="min-w-0 flex-1 rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-600"
              placeholder="e.g. Medical Imaging"
            />
            <button
              type="button"
              onClick={() => void addKeyword(true)}
              disabled={newExcluded.trim().length < 2}
              className="rounded-lg bg-slate-800 px-5 py-3 font-medium text-white hover:bg-slate-900 disabled:opacity-50"
            >
              Add Exclusion
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {excludedKeywords.length === 0 && (
              <p className="text-sm text-slate-500">
                No excluded keywords added yet.
              </p>
            )}

            {excludedKeywords.map((keyword) => (
              <span
                key={keyword.id}
                className="inline-flex items-center gap-2 rounded-full bg-red-50 px-3 py-2 text-sm text-red-800"
              >
                {keyword.keyword}
                <button
                  type="button"
                  onClick={() => void deleteKeyword(keyword.id)}
                  aria-label={`Remove ${keyword.keyword}`}
                  className="font-bold text-red-700 hover:text-red-900"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </section>

        <p className="mt-8 text-center text-sm text-slate-500">
          ZealWithin — Keep the researcher in you alive.
        </p>
      </div>
    </main>
  );
}
