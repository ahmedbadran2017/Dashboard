<template>
  <div>
    <div class="mb-3 flex items-center justify-between">
      <h1 class="text-[17px] font-extrabold">{{ i18n.t("deptsTitle") }}</h1>
    </div>
    <PeriodTabs class="mb-3" />

    <div v-if="res.loading && !list.length" class="py-8 text-center text-sm" style="color: var(--jy-mute)">{{ i18n.t("loading") }}</div>

    <div class="lg:grid lg:grid-cols-2 lg:gap-3 xl:grid-cols-3">
    <button
      v-for="(dp, i) in cards" :key="dp.id"
      class="card mb-2.5 block w-full p-3.5 text-start anim-stagger lg:mb-0"
      :style="{ animationDelay: (i * 45) + 'ms' }"
      @click="router.push('/ops/departments/' + dp.id)"
    >
      <div class="flex items-center gap-3">
        <div class="grid h-10 w-10 shrink-0 place-items-center rounded-[12px]" :style="{ background: dp.iconBg }">
          <Icon :name="dp.icon" :size="20" :style="{ color: dp.iconColor }" />
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-1.5">
            <span class="h-[7px] w-[7px] shrink-0 rounded-full" :style="{ background: dp.dot }" />
            <span class="truncate text-[14px] font-extrabold">{{ dp.name }}</span>
          </div>
          <div class="truncate text-[11px]" style="color: var(--jy-mute)">{{ dp.sub }}</div>
        </div>
        <div class="text-end">
          <div class="num text-[18px] font-extrabold leading-tight">{{ dp.kpi }}</div>
          <div class="num text-[11px] font-bold" :style="{ color: dp.trendColor }">{{ dp.trend }}</div>
        </div>
      </div>
      <!-- target progress -->
      <div class="mt-2.5 flex items-center gap-2">
        <div class="h-1 flex-1 overflow-hidden rounded-full" style="background: var(--jy-bg-2)">
          <div class="h-full rounded-full fill-x" :style="{ width: dp.target_pct + '%', background: dp.on_track ? 'var(--jy-green)' : 'var(--jy-orange)' }" />
        </div>
        <span class="whitespace-nowrap text-[10px]" style="color: var(--jy-mute)">{{ dp.targetLabel }}</span>
      </div>
    </button>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from "vue";
import { useRouter } from "vue-router";
import Icon from "@/components/Icon.vue";
import PeriodTabs from "@/components/PeriodTabs.vue";
import { createResource } from "@/lib/resource";
import { useI18n } from "@/i18n";
import { useDashboard } from "@/composables/useDashboard";
import { DEPT_META } from "@/i18n";
import { n, money, signed } from "@/lib/format";

const i18n = useI18n();
const router = useRouter();
const { periodKey, periodParams, refreshNonce } = useDashboard();

const res = createResource({ url: "ops_dashboard.api.departments.list_departments" });
const list = computed(() => res.data || []);

function load() { res.fetch(periodParams()); }
load();
watch(periodKey, load);
watch(refreshNonce, load);

const ACCENT = {
  green: { bg: "var(--jy-green-tint)", c: "var(--jy-green)" },
  orange: { bg: "var(--jy-orange-soft)", c: "var(--jy-orange)" },
  blue: { bg: "var(--jy-blue-tint)", c: "var(--jy-blue)" },
  red: { bg: "var(--jy-red-tint)", c: "var(--jy-red)" },
};

function kpiText(dp) {
  if (dp.kpi_unit === "%") return dp.kpi + "%";
  if (dp.kpi_unit === "MAD") return money(dp.kpi);
  return n(dp.kpi);
}

function subText(dp) {
  const m = {
    conf: i18n.L([`${n(dp.count)} من ${n(dp.total)} اتأكدوا`, `${n(dp.count)} of ${n(dp.total)} confirmed`]),
    wh: i18n.L(["أوردر اتحضر واتغلف", "orders picked & packed"]),
    disp: i18n.L([`خرجوا مع الكوريير — ${n(dp.stuck || 0)} عالق`, `dispatched — ${n(dp.stuck || 0)} stuck`]),
    del: i18n.L([`${n(dp.count)} أوردر اتسلّم`, `${n(dp.count)} delivered`]),
    ret: i18n.L([`${n(dp.count)} مرتجع مفتوح`, `${n(dp.count)} open returns`]),
    cod: i18n.L(["معلّق عند الكوريير", "pending at courier"]),
    mkt: i18n.L([`مبيعات — AOV ${n(dp.aov || 0)} MAD`, `sales — AOV ${n(dp.aov || 0)} MAD`]),
  };
  return m[dp.id] || "";
}

function trendText(dp) {
  if (["conf", "del", "ret"].includes(dp.id)) return signed(dp.trend) + "%";
  if (dp.id === "mkt") return signed(dp.trend) + "%";
  if (dp.id === "disp") return "⚠ " + n(dp.stuck || 0);
  if (dp.id === "cod") return i18n.L([`متأخر: ${money(dp.overdue || 0)}`, `overdue: ${money(dp.overdue || 0)}`]);
  return signed(dp.trend, 0);
}

function trendColor(dp) {
  if (dp.id === "ret") return dp.trend > 0 ? "var(--jy-red)" : "var(--jy-green)";
  if (dp.id === "disp") return "var(--jy-orange-ink)";
  if (dp.id === "cod") return "var(--jy-orange-ink)";
  return dp.trend < 0 ? "var(--jy-red)" : "var(--jy-green)";
}

const cards = computed(() =>
  list.value.map((dp) => {
    const meta = DEPT_META[dp.id] || { name: [dp.id, dp.id], icon: "box", accent: "orange" };
    const acc = ACCENT[meta.accent];
    return {
      ...dp,
      name: i18n.L(meta.name),
      icon: meta.icon,
      iconBg: acc.bg,
      iconColor: acc.c,
      dot: dp.on_track ? "var(--jy-green)" : "var(--jy-orange)",
      kpi: kpiText(dp),
      sub: subText(dp),
      trend: trendText(dp),
      trendColor: trendColor(dp),
      targetLabel: targetLabel(dp),
    };
  })
);

function targetLabel(dp) {
  const T = {
    conf: ["الهدف: 85%", "Target: 85%"],
    wh: ["الهدف: 120 أوردر", "Target: 120 orders"],
    disp: ["الهدف: 130 أوردر", "Target: 130 orders"],
    del: ["الهدف: 80%", "Target: 80%"],
    ret: ["الهدف: أقل من 8%", "Target: under 8%"],
    cod: ["الهدف: تسوية كل 48 س", "Target: settle every 48h"],
    mkt: ["الهدف: 35K/يوم", "Target: 35K/day"],
  };
  return i18n.L(T[dp.id] || ["", ""]);
}
</script>
