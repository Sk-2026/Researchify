
"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000/api/v1";

const PAPERS_PER_PAGE = 25;

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

type Notification = {
  id: string;
  paper_id: string;
  title: string;
  message: string;
  relevance_score: number;
  is_read: boolean;
  email_sent: boolean;
  created_at: string;
};

export default function DashboardPage() {
  const router = useRouter();

  const [profile, setProfile] = useState<Profile | null>(null);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [totalPapers, setTotalPapers] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [notificationError, setNotificationError] = useState("");
  const [markingRead, setMarkingRead] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const totalPages = Math.ceil(totalPapers / PAPERS_PER_PAGE);

  const loadNotifications = useCallback(async (token: string) => {
    try {
      const response = await fetch(`${API_URL}/notifications/`, {
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
        throw new Error("Could not load notifications.");
      }

      const data = await response.json();

      setNotifications(data.notifications ?? []);
      setUnreadCount(data.unread_count ?? 0);
      setNotificationError("");
    } catch (err) {
      setNotificationError(
        err instanceof Error
          ? err.message
          : "Could not load notifications."
      );
    }
  }, [router]);

  const loadDashboard = useCallback(
    async (token: string, page: number = 1): Promise<void> => {
      const headers = {
        Authorization: `Bearer ${token}`,
      };

      const offset = (page - 1) * PAPERS_PER_PAGE;

      const [profileResponse, papersResponse] = await Promise.all([
        fetch(`${API_URL}/profile`, { headers }),
        fetch(
          `${API_URL}/recommendations?limit=${PAPERS_PER_PAGE}&offset=${offset}`,
          { headers }
        ),
      ]);

      if (
        profileResponse.status === 401 ||
        papersResponse.status === 401
      ) {
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
      setTotalPapers(papersData.total ?? 0);
      setCurrentPage(page);

      await loadNotifications(token);
    },
    [router, loadNotifications]
  );

  useEffect(() => {
    const token = localStorage.getItem("zealwithin_token");

    if (!token) {
      router.replace("/");
      return;
    }

    loadDashboard(token, 1)
      .catch((err) => {
        setError(err.message || "Could not load dashboard.");
      })
      .finally(() => setLoading(false));
  }, [loadDashboard, router]);

  async function changePage(page: number) {
    if (page < 1 || page > totalPages || page === currentPage) {
      return;
    }

    const token = localStorage.getItem("zealwithin_token");

    if (!token) {
      router.replace("/");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await loadDashboard(token, page);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not load this page."
      );
    } finally {
      setLoading(false);
    }
  }

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

      await loadDashboard(token, 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Discovery failed."
      );
    } finally {
      setDiscovering(false);
    }
  }

  async function markNotificationAsRead(notificationId: string) {
    const token = localStorage.getItem("zealwithin_token");

    if (!token) {
      router.replace("/");
      return;
    }

    setMarkingRead(notificationId);

    try {
      const response = await fetch(
        `${API_URL}/notifications/${notificationId}/read`,
        {
          method: "PATCH",
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
        throw new Error("Could not mark notification as read.");
      }

      setNotifications((previous) =>
        previous.map((notification) =>
          notification.id === notificationId
            ? { ...notification, is_read: true }
            : notification
        )
      );

      setUnreadCount((previous) => Math.max(0, previous - 1));
    } catch (err) {
      setNotificationError(
        err instanceof Error
          ? err.message
          : "Could not update notification."
      );
    } finally {
      setMarkingRead(null);
    }
  }

  function logout() {
    localStorage.removeItem("zealwithin_token");
    router.replace("/");
  }

  function getVisiblePages() {
    const pages: number[] = [];
    const start = Math.max(1, currentPage - 2);
    const end = Math.min(totalPages, currentPage + 2);

    for (let page = start; page <= end; page++) {
      pages.push(page);
    }

    return pages;
  }

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center text-gray-600">
        Loading your research dashboard...
      </main>
    );
  }

  const firstPaper =
    totalPapers === 0
      ? 0
      : (currentPage - 1) * PAPERS_PER_PAGE + 1;

  const lastPaper = Math.min(
    currentPage * PAPERS_PER_PAGE,
    totalPapers
  );

  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[#214d70]">
              ZealWithin
            </h1>
            <p className="text-xs text-gray-500">
              Keep the researcher in you alive.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Notification bell */}
            <div className="relative">
              <button
                onClick={() => {
                  setNotificationOpen((previous) => !previous);
                  if (!notificationOpen) {
                    const token = localStorage.getItem("zealwithin_token");
                    if (token) loadNotifications(token);
                  }
                }}
                className="relative flex items-center justify-center rounded-lg border border-gray-200 bg-white p-2.5 text-gray-700 hover:bg-blue-50 transition"
                aria-label={`Notifications, ${unreadCount} unread`}
                aria-expanded={notificationOpen}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="21"
                  height="21"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
                  <path d="M10 21h4" />
                </svg>

                {unreadCount > 0 && (
                  <span className="absolute -right-2 -top-2 min-w-5 h-5 px-1 rounded-full bg-red-600 text-white text-xs font-bold flex items-center justify-center">
                    {unreadCount > 99 ? "99+" : unreadCount}
                  </span>
                )}
              </button>

              {notificationOpen && (
                <div className="absolute right-0 top-12 z-50 w-[min(90vw,400px)] bg-white border border-gray-200 rounded-xl shadow-xl overflow-hidden">
                  <div className="flex items-center justify-between p-4 border-b border-gray-100">
                    <div>
                      <h3 className="font-bold text-gray-900">
                        Notifications
                      </h3>
                      <p className="text-xs text-gray-500 mt-1">
                        {unreadCount} unread notification{unreadCount === 1 ? "" : "s"}
                      </p>
                    </div>

                    <button
                      onClick={() => setNotificationOpen(false)}
                      className="text-gray-400 hover:text-gray-700 text-xl"
                      aria-label="Close notifications"
                    >
                      ×
                    </button>
                  </div>

                  {notificationError && (
                    <p className="p-3 text-sm text-red-600">
                      {notificationError}
                    </p>
                  )}

                  <div className="max-h-[420px] overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-8 text-center">
                        <p className="text-sm font-semibold text-gray-700">
                          You're all caught up!
                        </p>
                        <p className="text-xs text-gray-500 mt-2">
                          New relevant research alerts will appear here.
                        </p>
                      </div>
                    ) : (
                      notifications.map((notification) => (
                        <div
                          key={notification.id}
                          className={`p-4 border-b border-gray-100 ${
                            notification.is_read ? "bg-white" : "bg-blue-50/60"
                          }`}
                        >
                          <div className="flex items-start gap-2">
                            {!notification.is_read && (
                              <span className="mt-1.5 w-2 h-2 rounded-full bg-blue-600 shrink-0" />
                            )}

                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-semibold text-gray-900">
                                {notification.title}
                              </p>

                              <p className="text-xs text-gray-600 mt-1 leading-5">
                                {notification.message}
                              </p>

                              <div className="flex flex-wrap items-center gap-2 mt-2">
                                <span className="text-xs font-semibold text-green-700">
                                  {Math.round(notification.relevance_score * 100)}% relevance
                                </span>

                                <span className="text-xs text-gray-400">
                                  {new Date(notification.created_at).toLocaleString()}
                                </span>
                              </div>

                              {!notification.is_read && (
                                <button
                                  onClick={() =>
                                    markNotificationAsRead(notification.id)
                                  }
                                  disabled={markingRead === notification.id}
                                  className="mt-3 text-xs font-semibold text-blue-700 hover:text-blue-900 disabled:opacity-50"
                                >
                                  {markingRead === notification.id
                                    ? "Updating..."
                                    : "Mark as read"}
                                </button>
                              )}

                              {notification.email_sent && (
                                <p className="text-xs text-gray-400 mt-2">
                                  Email notification sent
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={() => router.push("/settings")}
              className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition"
              aria-label="Open research settings"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06-.06-1.8 3.12-.09-.02a1.7 1.7 0 0 0-1.7.42l-.07.07h-3.6l-.07-.07a1.7 1.7 0 0 0-1.7-.42l-.09.02-1.8-3.12.06-.06A1.7 1.7 0 0 0 9.3 15l-.1-.03v-3.6l.1-.03v-3.6l-.1-.03a1.7 1.7 0 0 0-.34-1.88L8.9 9.4l1.8-3.12.09.02a1.7 1.7 0 0 0 1.7-.42l.07-.07h3.6l.07.07a1.7 1.7 0 0 0 1.7.42l.09-.02 1.8 3.12-.06.06A1.7 1.7 0 0 0 19.3 11.3l.1.03v3.6z" />
              </svg>
              Settings
            </button>

            <button
              onClick={logout}
              className="text-sm font-semibold text-gray-600 hover:text-red-600"
            >
              Sign out
            </button>
          </div>
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
                <p className="text-sm text-gray-500">
                  Research domain
                </p>
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
            {discovering
              ? "Discovering papers..."
              : "Discover new papers"}
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

        {totalPapers > 0 && (
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-5">
            <p className="text-sm font-medium text-gray-700">
              Showing {firstPaper}–{lastPaper} of {totalPapers} papers
            </p>
            <p className="text-xs text-gray-500">
              Sorted by relevance: highest to lowest
            </p>
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
              className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm"
            >
              <div className="flex flex-col md:flex-row md:justify-between gap-3">
                <h4 className="text-lg font-bold text-gray-900">
                  {paper.title}
                </h4>

                {typeof paper.final_score === "number" && (
                  <span className="text-sm font-semibold text-green-700 whitespace-nowrap">
                    {Math.round(paper.final_score * 100)}% relevance
                  </span>
                )}
              </div>

              <div className="flex flex-wrap gap-3 text-xs text-gray-500 mt-3">
                {paper.publication_date && (
                  <span>Published: {paper.publication_date}</span>
                )}
                {paper.venue && <span>{paper.venue}</span>}
              </div>

              {paper.authors && paper.authors.length > 0 && (
                <p className="text-sm text-gray-600 mt-3">
                  <strong>Authors:</strong> {paper.authors.join(", ")}
                </p>
              )}

              {paper.matched_interest && (
                <div className="mt-3">
                  <span className="bg-blue-50 text-blue-700 rounded-full px-3 py-1 text-xs font-medium">
                    Matched interest: {paper.matched_interest}
                  </span>
                </div>
              )}

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

        {totalPages > 1 && (
          <nav
            className="flex flex-wrap items-center justify-center gap-2 mt-10 mb-6"
            aria-label="Research paper pagination"
          >
            <button
              onClick={() => changePage(currentPage - 1)}
              disabled={currentPage === 1 || loading}
              className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-blue-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            {currentPage > 3 && (
              <>
                <button
                  onClick={() => changePage(1)}
                  disabled={loading}
                  className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 hover:bg-blue-50"
                >
                  1
                </button>
                {currentPage > 4 && (
                  <span className="px-1 text-gray-400">...</span>
                )}
              </>
            )}

            {getVisiblePages().map((page) => (
              <button
                key={page}
                onClick={() => changePage(page)}
                disabled={loading}
                aria-current={page === currentPage ? "page" : undefined}
                className={`rounded-lg border px-3 py-2 text-sm font-semibold transition ${
                  page === currentPage
                    ? "border-blue-600 bg-blue-600 text-white"
                    : "border-gray-200 bg-white text-gray-700 hover:bg-blue-50"
                }`}
              >
                {page}
              </button>
            ))}

            {currentPage < totalPages - 2 && (
              <>
                {currentPage < totalPages - 3 && (
                  <span className="px-1 text-gray-400">...</span>
                )}
                <button
                  onClick={() => changePage(totalPages)}
                  disabled={loading}
                  className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 hover:bg-blue-50"
                >
                  {totalPages}
                </button>
              </>
            )}

            <button
              onClick={() => changePage(currentPage + 1)}
              disabled={currentPage === totalPages || loading}
              className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-blue-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </nav>
        )}

        {totalPages > 1 && (
          <p className="text-center text-xs text-gray-500 mb-8">
            Page {currentPage} of {totalPages}
          </p>
        )}
      </div>
    </main>
  );
}
