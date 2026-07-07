// Minimal frappe-ui-compatible data layer (no frappe-ui package dependency — the
// same approach the other Justyol portals use, so standalone Vite dev has zero
// CJS-interop friction). Calls the exact `/api/method/<dotted.path>` endpoints, so
// it behaves identically against a real Frappe bench. When no bench is reachable
// (standalone preview) it answers from the live snapshot in lib/demo.js.
import { reactive } from "vue";
import { isDemo, demoResolve } from "./demo";

function getCsrf() {
  return (typeof window !== "undefined" && (window.csrf_token || window.frappe?.csrf_token)) || "";
}

export async function call(method, params = {}) {
  if (isDemo()) return demoResolve(method, params);
  const res = await fetch(`/api/method/${method}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": getCsrf(),
      "X-Requested-With": "XMLHttpRequest",
    },
    body: JSON.stringify(params || {}),
  });
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const j = await res.json();
      if (j._server_messages) msg = JSON.parse(JSON.parse(j._server_messages)[0]).message;
      else if (j.message) msg = j.message;
    } catch (_) {}
    throw new Error(msg);
  }
  const json = await res.json();
  return json.message; // Frappe wraps whitelisted returns in `message`
}

export function createResource(options) {
  const state = reactive({ data: options.initial ?? null, loading: false, error: null });
  async function fetch(extraParams) {
    state.loading = true;
    state.error = null;
    try {
      const params = { ...(options.params || {}), ...(extraParams || {}) };
      const raw = await call(options.url, params);
      state.data = options.transform ? options.transform(raw) : raw;
      options.onSuccess && options.onSuccess(state.data);
      return state.data;
    } catch (e) {
      state.error = e;
      options.onError && options.onError(e);
      return null;
    } finally {
      state.loading = false;
    }
  }
  state.fetch = fetch;
  state.reload = fetch;
  if (options.auto) fetch();
  return state;
}
