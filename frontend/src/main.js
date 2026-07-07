import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./index.css";
import { applyThemeToRoot } from "./composables/useTheme";
import { applyLangToRoot } from "./i18n";

applyThemeToRoot();
applyLangToRoot();

createApp(App).use(router).mount("#app");
