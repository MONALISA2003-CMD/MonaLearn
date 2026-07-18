/**
 * MonaLearn auth helper — shared across dashboard.html, admin.html, and
 * login.html. Plain script, no bundler, so it's just included via
 * <script src="auth.js"></script> on any page that needs it.
 *
 * IMPORTANT if you're previewing these files as a Claude.ai artifact:
 * localStorage is sandboxed/unavailable inside Claude.ai's artifact
 * preview iframe, so token persistence here will silently no-op there.
 * This is expected — it works normally once these files are actually
 * deployed (Vercel, or just opened from disk), which is the point of
 * this file existing at all. Every page that uses this also has a
 * "Continue in demo mode" fallback specifically so the artifact preview
 * still shows something useful even when storage doesn't persist.
 */
const MonaAuth = (() => {
  const TOKEN_KEY = "monalearn_token";
  const API_BASE_URL = "https://monalearn-api.onrender.com";

  function getToken() {
    try { return localStorage.getItem(TOKEN_KEY); } catch (e) { return null; }
  }
  function setToken(token) {
    try { localStorage.setItem(TOKEN_KEY, token); } catch (e) { /* storage unavailable, e.g. artifact preview */ }
  }
  function clearToken() {
    try { localStorage.removeItem(TOKEN_KEY); } catch (e) { /* no-op */ }
  }

  function isDemoMode() {
    return new URLSearchParams(window.location.search).get("demo") === "1";
  }

  /**
   * Fetch wrapper that attaches the bearer token automatically.
   * Throws on network failure or non-OK response so callers can decide
   * what to do (fall back to demo data, redirect to login, etc.).
   */
  async function authFetch(path, options = {}) {
    const token = getToken();
    const headers = Object.assign({}, options.headers, token ? { Authorization: `Bearer ${token}` } : {});
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      signal: options.signal || AbortSignal.timeout(3000),
    });
    if (res.status === 401) {
      clearToken();
      const err = new Error("Unauthorized");
      err.status = 401;
      throw err;
    }
    if (!res.ok) {
      const err = new Error("Request failed: " + res.status);
      err.status = res.status;
      throw err;
    }
    return res.json();
  }

  /**
   * Call at the top of a page that requires login. Redirects to login.html
   * if there's no token and demo mode wasn't explicitly requested via
   * ?demo=1. Returns true if the page should proceed to load normally
   * (either authenticated or in demo mode), false if it's redirecting away.
   */
  function requireAuthOrDemo() {
    if (isDemoMode()) return true;
    if (getToken()) return true;
    window.location.href = "login.html?next=" + encodeURIComponent(window.location.pathname);
    return false;
  }

  async function getCurrentUser() {
    return authFetch("/api/auth/me");
  }

  function logout(redirectTo = "login.html") {
    clearToken();
    window.location.href = redirectTo;
  }

  return { getToken, setToken, clearToken, isDemoMode, authFetch, requireAuthOrDemo, getCurrentUser, logout, API_BASE_URL };
})();
