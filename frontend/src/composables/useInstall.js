// PWA install-prompt state.
//
// Android/Chrome fires `beforeinstallprompt` when installability criteria are
// met (manifest + SW + HTTPS). We capture it and expose promptInstall() so the
// UI can show its own "ثبّت التطبيق" button — the native mini-infobar timing is
// unreliable. iOS Safari has NO install event at all, so there we show a
// how-to banner (Share → Add to Home Screen) instead. Nothing is shown when
// already running installed (standalone) or after the user dismissed it.
import { ref, computed } from "vue";

const DISMISS_KEY = "ops.installDismissed";

const deferredPrompt = ref(null);
const dismissed = ref(
  typeof localStorage !== "undefined" && localStorage.getItem(DISMISS_KEY) === "1"
);
const installed = ref(false);

const isStandalone = () =>
  (typeof window !== "undefined" &&
    (window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true));

const isIos = () =>
  typeof navigator !== "undefined" &&
  /iphone|ipad|ipod/i.test(navigator.userAgent) &&
  !window.MSStream;

// Must be registered EARLY (main.js) — the event often fires before the app mounts.
export function setupInstallCapture() {
  if (typeof window === "undefined") return;
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt.value = e;
  });
  window.addEventListener("appinstalled", () => {
    installed.value = true;
    deferredPrompt.value = null;
  });
}

export function useInstall() {
  const forced = typeof window !== "undefined" && window.__OPS_FORCE_INSTALL__ === true;
  const show = computed(() => {
    if (forced) return true;
    if (dismissed.value || installed.value || isStandalone()) return false;
    return !!deferredPrompt.value || isIos();
  });
  const ios = computed(() => (forced ? window.__OPS_FORCE_IOS__ === true : isIos() && !deferredPrompt.value));

  async function promptInstall() {
    const p = deferredPrompt.value;
    if (!p) return;
    p.prompt();
    const choice = await p.userChoice.catch(() => null);
    if (choice && choice.outcome === "accepted") installed.value = true;
    deferredPrompt.value = null;
  }

  function dismiss() {
    dismissed.value = true;
    try { localStorage.setItem(DISMISS_KEY, "1"); } catch (_) {}
  }

  return { show, ios, promptInstall, dismiss };
}
