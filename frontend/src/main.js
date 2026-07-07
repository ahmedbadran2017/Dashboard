import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./index.css";
import { applyThemeToRoot } from "./composables/useTheme";
import { applyLangToRoot } from "./i18n";
import { setupInstallCapture } from "./composables/useInstall";

applyThemeToRoot();
applyLangToRoot();
setupInstallCapture(); // must run before mount — beforeinstallprompt fires early

createApp(App).use(router).mount("#app");
