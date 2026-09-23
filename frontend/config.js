// Desi Card Games - Dynamic Configuration & Backend Manager
// Supports seamless switching between Render Cloud Backend, Localhost, and Custom URLs.

const DEFAULT_RENDER_BACKEND = "https://sagan-czyf.onrender.com";
const STORAGE_KEY_BACKEND = "DESI_GAMES_BACKEND_URL";

/**
 * Returns the currently active backend base URL without trailing slash.
 */
function getBackendUrl() {
    // 1. URL Query Parameter Override (?backend=...)
    try {
        const params = new URLSearchParams(window.location.search);
        const qBackend = params.get("backend");
        if (qBackend && qBackend.trim()) {
            return qBackend.trim().replace(/\/+$/, "");
        }
    } catch (e) {}

    // 2. Saved User/Admin Preference in localStorage
    try {
        const saved = localStorage.getItem(STORAGE_KEY_BACKEND);
        if (saved && saved.trim()) {
            return saved.trim().replace(/\/+$/, "");
        }
    } catch (e) {}

    // 3. Localhost automatic detection (if developing locally and no manual override set)
    const hostname = window.location.hostname;
    if (hostname === "localhost" || hostname === "127.0.0.1") {
        return window.location.origin.replace(/\/+$/, "");
    }

    // 4. Default production backend on Render
    return DEFAULT_RENDER_BACKEND.replace(/\/+$/, "");
}

/**
 * Saves a custom backend URL in localStorage.
 */
function setBackendUrl(url) {
    if (!url || !url.trim()) {
        resetBackendUrl();
        return;
    }
    const clean = url.trim().replace(/\/+$/, "");
    try {
        localStorage.setItem(STORAGE_KEY_BACKEND, clean);
    } catch (e) {
        console.warn("Could not save backend URL to localStorage:", e);
    }
}

/**
 * Resets backend URL to default.
 */
function resetBackendUrl() {
    try {
        localStorage.removeItem(STORAGE_KEY_BACKEND);
    } catch (e) {}
}

/**
 * Pings the backend health endpoint with a timeout.
 * @param {string} [baseUrl] - Backend base URL. Defaults to getBackendUrl().
 * @param {number} [timeoutMs=5000] - Request timeout in ms.
 * @returns {Promise<{ok: boolean, data?: any, error?: string, elapsedMs: number}>}
 */
async function checkBackendHealth(baseUrl = getBackendUrl(), timeoutMs = 5000) {
    const start = Date.now();
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const res = await fetch(`${baseUrl}/api/health`, {
            method: "GET",
            headers: { "Accept": "application/json" },
            signal: controller.signal,
            cache: "no-store"
        });
        clearTimeout(timer);
        const elapsed = Date.now() - start;

        if (res.ok) {
            const data = await res.json();
            return { ok: true, data, elapsedMs: elapsed };
        } else {
            return { ok: false, error: `HTTP ${res.status}`, elapsedMs: elapsed };
        }
    } catch (err) {
        clearTimeout(timer);
        const elapsed = Date.now() - start;
        return {
            ok: false,
            error: err.name === "AbortError" ? "Timeout" : (err.message || "Network Error"),
            elapsedMs: elapsed
        };
    }
}

// Export to window for global access
window.DEFAULT_RENDER_BACKEND = DEFAULT_RENDER_BACKEND;
window.getBackendUrl = getBackendUrl;
window.setBackendUrl = setBackendUrl;
window.resetBackendUrl = resetBackendUrl;
window.checkBackendHealth = checkBackendHealth;
