
"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000/api/v1";

type Profile = {
  domain: string;
  description?: string;
  keywords: {
    id: string;
    keyword: string;
    is_excluded: boolean;
  }[];
};

type Paper = {
  id: string;
  title: string;
  abstract?: string | null;
  publication_date?: string | null;
  authors?: string[];
  venue?: string | null;
  final_score?: number;
  matched_interest?: string | null;
  doi?: string | null;
};

export default function DashboardPage() {
  const router = useRouter();

  const [profile, setProfile] = useState<Profile | null>(null);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");


  const loadDashboard = useCallback(async (token: string): Promise<void> => {
    const headers = {
      Authorization: `Bearer ${token}`,
    };

    const [profileResponse, papersResponse] = await Promise.all([
      fetch(`${API_URL}/profile`, { headers }),
      fetch(`${API_URL}/recommendations`, { headers }),
    ]);

    if (profileResponse.status === 401 || papersResponse.status === 401) {
      localStorage.removeItem("zealwithin_token");
      router.replace("/");
      return;
    }

    if (profileResponse.status === 404) {
      router.replace("/onboarding");
      return;
    }

    if (!profileResponse.ok) {
      throw new Error("Could not load your research profile.");
    }

    if (!papersResponse.ok) {
      throw new Error("Could not load research recommendations.");
    }

    const profileData = await profileResponse.json();
    const papersData = await papersResponse.json();

    setProfile(profileData);
    setPapers(papersData.recommendations ?? []);
    }, [router]);

    useEffect(() => {
    const token = localStorage.getItem("zealwithin_token");

    if (!token) {
        router.replace("/");
        return;
    }

    loadDashboard(token)
        .catch((err) => {
        setError(err.message || "Could not load dashboard.");
        })
        .finally(() => setLoading(false));
    }, [loadDashboard]);
  async function runDiscovery() {
    const token = localStorage.getItem("zealwithin_token");

    if (!token) {
      router.replace("/");
      return;
    }

    setDiscovering(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/discovery/run`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Discovery failed.");
      }

      setMessage(
        `Discovery complete! Found ${data.discovered_count} papers and added ${data.inserted_count} new papers.`
      );

      await loadDashboard(token);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Discovery failed."
      );
    } finally {
      setDiscovering(false);
    }
  }

  function logout() {
    localStorage.removeItem("zealwithin_token");
    router.replace("/");
  }

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center text-gray-600">
        Loading your research dashboard...
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#214d70]">
              ZealWithin
            </h1>
            <p className="text-xs text-gray-500">
              Keep the researcher in you alive.
            </p>
          </div>

          <button
            onClick={logout}
            className="text-sm font-semibold text-gray-600 hover:text-red-600"
          >
            Sign out
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-10">
        <section className="mb-10">
          <p className="text-sm font-semibold text-blue-600 mb-2">
            YOUR RESEARCH SPACE
          </p>
          <h2 className="text-3xl font-bold text-gray-900">
            Welcome to your dashboard.
          </h2>
          <p className="text-gray-500 mt-2">
            Discover research that matters to you.
          </p>
        </section>

        {profile && (
          <section className="bg-white rounded-2xl border border-gray-100 p-6 mb-8">
            <div className="flex flex-col md:flex-row md:justify-between gap-4">
              <div>
                <p className="text-sm text-gray-500">Research domain</p>
                <h3 className="text-xl font-bold text-gray-900 mt-1">
                  {profile.domain}
                </h3>
                {profile.description && (
                  <p className="text-gray-500 mt-2">
                    {profile.description}
                  </p>
                )}
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">
                  Your research interests
                </p>
                <div className="flex flex-wrap gap-2">
                  {profile.keywords
                    ?.filter((item) => !item.is_excluded)
                    .map((item) => (
                      <span
                        key={item.id}
                        className="bg-blue-50 text-blue-700 rounded-full px-3 py-1 text-sm"
                      >
                        {item.keyword}
                      </span>
                    ))}
                </div>
              </div>
            </div>
          </section>
        )}

        <section className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">
              Recommended papers
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Research selected according to your interests.
            </p>
          </div>

          <button
            onClick={runDiscovery}
            disabled={discovering}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold rounded-xl px-6 py-3"
          >
            {discovering ? "Discovering papers..." : "Discover new papers"}
          </button>
        </section>

        {message && (
          <div className="bg-green-50 text-green-700 rounded-xl p-4 mb-5 text-sm">
            {message}
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-700 rounded-xl p-4 mb-5 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {papers.length === 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 p-10 text-center">
              <h4 className="text-lg font-semibold text-gray-800">
                No recommendations yet
              </h4>
              <p className="text-gray-500 mt-2">
                Discover papers to start building your research feed.
              </p>
            </div>
          )}

          {papers.map((paper) => (
            <article
              key={paper.id}
              className="bg-white rounded-2xl border border-gray-100 p-6"
            >
              <h4 className="text-lg font-bold text-gray-900">
                {paper.title}
              </h4>

              <div className="flex flex-wrap gap-3 text-xs text-gray-500 mt-3">
                {paper.publication_date && (
                  <span>{paper.publication_date}</span>
                )}
                {paper.venue && <span>{paper.venue}</span>}
                {paper.matched_interest && (
                  <span className="text-blue-600">
                    Matched: {paper.matched_interest}
                  </span>
                )}
              </div>

              {paper.abstract && (
                <p className="text-sm text-gray-600 leading-6 mt-4">
                  {paper.abstract}
                </p>
              )}

              {paper.doi && (
                <p className="text-xs text-gray-400 mt-3">
                  DOI: {paper.doi}
                </p>
              )}
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
