<template>
  <div class="flex min-h-screen" style="background: var(--jy-bg)">
    <!-- ── Desktop sidebar (lg+) ── -->
    <aside
      class="sticky top-0 hidden h-screen w-60 shrink-0 flex-col lg:flex"
      style="background: var(--jy-surface); border-inline-end: 1px solid var(--jy-line)"
    >
      <div class="px-5 pb-4 pt-6">
        <img :src="logo" alt="Justyol" class="h-6 w-auto" />
        <div class="mt-1 text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("subtitle") }}</div>
      </div>
      <nav class="flex-1 space-y-1 px-3">
        <button
          v-for="tb in tabs" :key="tb.id"
          class="flex w-full items-center gap-3 rounded-[10px] px-3 py-2.5 text-start text-[14px] font-bold transition"
          :style="active === tb.id
            ? 'background: var(--jy-orange-soft); color: var(--jy-orange-ink)'
            : 'color: var(--jy-mute)'"
          @click="go(tb.to)"
        >
          <Icon :name="tb.icon" :size="20" :stroke="active === tb.id ? 2 : 1.8"
                :style="{ color: active === tb.id ? 'var(--jy-orange)' : 'var(--jy-mute)' }" />
          <span>{{ tb.label }}</span>
          <span v-if="tb.id === 'alerts' && badge > 0"
                class="num ms-auto grid h-5 min-w-5 place-items-center rounded-full px-1 text-[10px] font-bold text-white"
                style="background: var(--jy-red)">{{ badge }}</span>
        </button>
      </nav>
      <div class="flex items-center gap-2 border-t p-3" style="border-color: var(--jy-line)">
        <button class="grid h-9 w-9 place-items-center rounded-full" style="background: var(--jy-bg-2)" @click="theme.toggle" aria-label="theme">
          <Icon :name="theme.theme.value === 'dark' ? 'sun' : 'moon'" :size="17" style="color: var(--jy-ink)" />
        </button>
        <button class="h-9 rounded-full px-3 text-xs font-bold" style="background: var(--jy-bg-2); color: var(--jy-ink)" @click="i18n.toggle">
          {{ i18n.isAr.value ? "EN" : "ع" }}
        </button>
        <span class="num ms-auto text-[11px]" style="color: var(--jy-mute)">{{ dateStr }}</span>
      </div>
    </aside>

    <!-- ── Main column ── -->
    <div class="flex min-w-0 flex-1 flex-col">
      <!-- Mobile header (below lg) -->
      <header
        class="sticky top-0 z-20 flex items-center justify-between px-4 py-3 lg:hidden"
        style="background: var(--jy-surface); border-bottom: 1px solid var(--jy-line); padding-top: max(12px, env(safe-area-inset-top))"
      >
        <div class="flex items-center gap-2">
          <button class="grid h-[34px] w-[34px] place-items-center rounded-full" style="background: var(--jy-bg-2)" @click="theme.toggle" aria-label="theme">
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
        <div class="flex flex-col items-end" :class="{ 'items-start': !i18n.isAr.value }">
          <img :src="logo" alt="Justyol" class="h-[22px] w-auto" />
          <span class="mt-0.5 text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("subtitle") }} · {{ dateStr }}</span>
        </div>
      </header>

      <!-- Screen content -->
      <main class="flex-1 overflow-y-auto px-4 pb-28 pt-3 lg:px-8 lg:py-8">
        <div class="mx-auto w-full max-w-[440px] lg:max-w-5xl">
          <router-view v-slot="{ Component }">
            <component :is="Component" :key="routeKey" class="anim-screen" />
          </router-view>
        </div>
      </main>
    </div>

    <!-- PWA install banner (Android: real prompt · iOS: add-to-home-screen how-to) -->
    <InstallBanner />

    <!-- Bottom tab bar (mobile only) -->
    <nav
      class="fixed inset-x-0 bottom-0 z-30 mx-auto flex w-full max-w-[440px] justify-around lg:hidden"
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
import InstallBanner from "@/components/InstallBanner.vue";
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
  { id: "depts", to: "/ops/departments", icon: "depts", label: i18n.isAr.value ? "الأقسام" : "Departments" },
  { id: "orders", to: "/ops/orders", icon: "orders", label: i18n.isAr.value ? "الأوردرات" : "Orders" },
  { id: "team", to: "/ops/team", icon: "team", label: i18n.isAr.value ? "الفريق" : "Team" },
  { id: "finance", to: "/ops/finance", icon: "cash", label: i18n.isAr.value ? "المالية" : "Finance" },
  { id: "alerts", to: "/ops/alerts", icon: "alerts", label: i18n.isAr.value ? "التنبيهات" : "Alerts" },
]);

function go(to) { if (route.path !== to) router.push(to); }
function goAlerts() { go("/ops/alerts"); }

const badge = ref(0);
const badgeRes = createResource({ url: "ops_dashboard.api.alerts.badge_count" });
onMounted(async () => { badge.value = (await badgeRes.fetch()) || 0; });
</script>
