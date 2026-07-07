<template>
  <div class="mx-auto flex min-h-screen w-full max-w-[440px] flex-col" style="background: var(--jy-bg)">
    <!-- Header -->
    <header
      class="sticky top-0 z-20 flex items-center justify-between px-4 py-3"
      style="background: var(--jy-surface); border-bottom: 1px solid var(--jy-line); padding-top: max(12px, env(safe-area-inset-top))"
    >
      <!-- controls (end side in RTL = visually left) -->
      <div class="flex items-center gap-2">
        <button class="grid h-[34px] w-[34px] place-items-center rounded-full" style="background: var(--jy-bg-2)" @click="theme.toggle" :aria-label="'theme'">
          <Icon :name="theme.theme.value === 'dark' ? 'sun' : 'moon'" :size="17" style="color: var(--jy-ink)" />
        </button>
        <button class="h-[34px] rounded-full px-3 text-xs font-bold" style="background: var(--jy-bg-2); color: var(--jy-ink)" @click="i18n.toggle">
          {{ i18n.isAr.value ? "EN" : "ع" }}
        </button>
        <button class="relative grid h-[34px] w-[34px] place-items-center rounded-full" style="background: var(--jy-bg-2)" @click="goAlerts" aria-label="alerts">
          <Icon name="bell" :size="17" style="color: var(--jy-ink)" />
          <span
            v-if="badge > 0"
            class="num absolute -top-1 grid h-[15px] min-w-[15px] place-items-center rounded-full px-1 text-[9px] font-bold text-white"
            :style="{ background: 'var(--jy-red)', ...(i18n.isAr.value ? { left: '-2px' } : { right: '-2px' }) }"
          >{{ badge }}</span>
        </button>
      </div>
      <!-- brand -->
      <div class="flex flex-col items-end" :class="{ 'items-start': !i18n.isAr.value }">
        <img :src="logo" alt="Justyol" class="h-[22px] w-auto" />
        <span class="mt-0.5 text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("subtitle") }} · {{ dateStr }}</span>
      </div>
    </header>

    <!-- Screen content -->
    <main class="flex-1 overflow-y-auto px-4 pb-28 pt-3">
      <router-view v-slot="{ Component }">
        <component :is="Component" :key="routeKey" class="anim-screen" />
      </router-view>
    </main>

    <!-- Bottom tab bar -->
    <nav
      class="fixed inset-x-0 bottom-0 z-30 mx-auto flex w-full max-w-[440px] justify-around"
      style="background: var(--jy-surface); border-top: 1px solid var(--jy-line); box-shadow: var(--shadow-nav); padding: 6px 6px calc(20px + env(safe-area-inset-bottom))"
    >
      <button
        v-for="tb in tabs" :key="tb.id"
        class="tap flex flex-1 flex-col items-center gap-1 py-1"
        @click="go(tb.to)"
      >
        <Icon :name="tb.icon" :size="21" :stroke="active === tb.id ? 2 : 1.8" :key="tb.id + active" :class="{ 'anim-pop': active === tb.id }" :style="{ color: active === tb.id ? 'var(--jy-orange)' : 'var(--jy-mute)' }" />
        <span class="text-[10px]" :style="{ color: active === tb.id ? 'var(--jy-orange)' : 'var(--jy-mute)', fontWeight: active === tb.id ? 800 : 500 }">{{ tb.label }}</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icon from "@/components/Icon.vue";
import { useTheme } from "@/composables/useTheme";
import { useI18n } from "@/i18n";
import { createResource } from "@/lib/resource";

const theme = useTheme();
const i18n = useI18n();
const route = useRoute();
const router = useRouter();

const logo = computed(() =>
  theme.theme.value === "dark"
    ? "/assets/ops_dashboard/img/logo-justyol-white.png"
    : "/assets/ops_dashboard/img/logo-justyol.png"
);

const dateStr = computed(() =>
  new Date().toLocaleDateString(i18n.isAr.value ? "ar-EG" : "en-GB", { day: "numeric", month: "long", year: "numeric" })
);

const active = computed(() => route.meta.tab || "home");
const routeKey = computed(() => route.name === "DepartmentDetail" ? "depts" : route.path);

const tabs = computed(() => [
  { id: "home", to: "/ops/home", icon: "home", label: i18n.isAr.value ? "الرئيسية" : "Home" },
  { id: "depts", to: "/ops/departments", icon: "depts", label: i18n.isAr.value ? "الأقسام" : "Depts" },
  { id: "orders", to: "/ops/orders", icon: "orders", label: i18n.isAr.value ? "الأوردرات" : "Orders" },
  { id: "team", to: "/ops/team", icon: "team", label: i18n.isAr.value ? "الفريق" : "Team" },
  { id: "alerts", to: "/ops/alerts", icon: "alerts", label: i18n.isAr.value ? "التنبيهات" : "Alerts" },
]);

function go(to) { if (route.path !== to) router.push(to); }
function goAlerts() { go("/ops/alerts"); }

const badge = ref(0);
const badgeRes = createResource({ url: "ops_dashboard.api.alerts.badge_count" });
onMounted(async () => { badge.value = (await badgeRes.fetch()) || 0; });
</script>
