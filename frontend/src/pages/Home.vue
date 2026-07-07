<template>
  <div>
    <!-- Trust line -->
    <div class="mb-3 flex items-center justify-between">
      <div class="flex items-center gap-1.5">
        <span class="inline-block h-1.5 w-1.5 rounded-full" style="background: var(--jy-green)" />
        <span class="text-[11px] whitespace-nowrap" style="color: var(--jy-mute)">{{ i18n.t("live") }} · <span class="num">{{ nowTime }}</span></span>
      </div>
      <button class="flex items-center gap-1 text-[11px] font-bold" style="color: var(--jy-blue)" @click="reload">
        <Icon name="refresh" :size="12" style="color: var(--jy-blue)" />{{ i18n.t("refresh") }}
      </button>
    </div>

    <!-- Period segmented control -->
    <PeriodTabs class="mb-3" />

    <!-- Hero KPI card -->
    <div class="mb-3 p-[18px]" style="background: #1a1a1a; border: 1px solid rgba(255,255,255,0.09); border-radius: 18px">
      <div class="flex items-start justify-between">
        <div>
          <div class="text-[12px]" style="color: rgba(255,255,255,0.6)">{{ i18n.t("orders") }}</div>
          <div class="num text-[36px] font-extrabold leading-none text-white">{{ shownOrders }}</div>
          <div class="num mt-1 text-[12px] font-bold" :style="{ color: deltaPos ? '#5ad48a' : '#ff8f7a' }">
            {{ signed(d.orders_delta_pct) }}% <span style="color: rgba(255,255,255,0.55)">{{ cmpLabel }}</span>
          </div>
        </div>
        <div class="text-end">
          <div class="text-[12px]" style="color: rgba(255,255,255,0.6)">{{ i18n.t("salesValue") }}</div>
          <div class="num text-[24px] font-extrabold" style="color: var(--jy-orange)">{{ money(d.value) }}</div>
          <div class="text-[11px]" style="color: rgba(255,255,255,0.45)">{{ d.currency }}</div>
        </div>
      </div>

      <!-- 7-day bars -->
      <div class="mt-4 flex items-end justify-between gap-1.5" style="height: 46px">
        <div v-for="(b, i) in weekBars" :key="i" class="flex flex-1 flex-col items-center justify-end gap-1" style="height: 46px">
          <div class="grow-up w-full rounded-t" :style="{ height: b.h, background: b.color, animationDelay: b.delay }" />
          <span class="text-[9px]" style="color: rgba(255,255,255,0.5)">{{ b.label }}</span>
        </div>
      </div>

      <!-- Forecast -->
      <div v-if="d.forecast" class="mt-3 flex items-center gap-2 rounded-[10px] px-3 py-2" style="background: rgba(255,255,255,0.07)">
        <Icon name="trend" :size="15" style="color: var(--jy-orange)" />
        <span class="text-[12px]" style="color: rgba(255,255,255,0.8)">
          {{ i18n.t("forecast") }} <span class="num font-bold" style="color: var(--jy-orange)">~{{ n(d.forecast) }}</span> {{ i18n.t("forecastUnit") }}
        </span>
      </div>
    </div>

    <!-- Loading / error -->
    <div v-if="res.loading && !d.orders" class="py-8 text-center text-sm" style="color: var(--jy-mute)">{{ i18n.t("loading") }}</div>

    <template v-if="d.orders !== undefined">
      <!-- Order funnel -->
      <div class="card mb-3 p-4">
        <div class="mb-3 text-[13px] font-extrabold">{{ i18n.t("funnelTitle") }}</div>
        <div v-for="(f, i) in funnel" :key="f.key" class="mb-2.5 flex items-center gap-2 last:mb-0">
          <span class="w-[74px] shrink-0 text-[12px]" style="color: var(--jy-text-2)">{{ f.label }}</span>
          <div class="relative h-[18px] flex-1 overflow-hidden rounded-[5px]" style="background: var(--jy-bg-2)">
            <div class="fill-x h-full rounded-[5px]" :style="{ width: f.w, background: f.color, animationDelay: f.delay }" />
          </div>
          <span class="num w-9 text-end text-[12px] font-extrabold">{{ n(f.count) }}</span>
        </div>
      </div>

      <!-- Rate cards 2x2 -->
      <div class="mb-3 grid grid-cols-2 gap-2.5">
        <div v-for="(r, i) in rateCards" :key="r.key" class="card p-3 anim-stagger" :style="{ animationDelay: (i * 60) + 'ms' }">
          <div class="mb-2 grid h-[22px] w-[22px] place-items-center rounded-[7px]" :style="{ background: r.iconBg }">
            <Icon :name="r.icon" :size="12" :style="{ color: r.iconColor }" />
          </div>
          <div class="text-[11px]" style="color: var(--jy-mute)">{{ r.label }}</div>
          <div class="num text-[22px] font-extrabold leading-tight">{{ r.value }}</div>
          <div class="num text-[11px] font-bold" :style="{ color: r.deltaColor }">{{ r.delta }}</div>
        </div>
      </div>

      <!-- COD -->
      <div class="card mb-3 p-4">
        <div class="mb-3 flex items-center justify-between">
          <span class="text-[13px] font-extrabold">{{ i18n.t("codTitle") }}</span>
          <span class="pill px-2 py-0.5 text-[10px] font-bold" style="background: var(--jy-green-tint); color: var(--jy-green)">Cathedis</span>
        </div>
        <div class="grid grid-cols-2 gap-2.5">
          <div class="rounded-[10px] p-3" style="background: var(--jy-green-tint)">
            <div class="text-[11px]" style="color: var(--jy-green)">{{ i18n.t("codCollected") }}</div>
            <div class="num text-[18px] font-extrabold" style="color: var(--jy-green)">{{ moneyFull(d.cod.collected) }} <span class="text-[11px]">MAD</span></div>
          </div>
          <div class="rounded-[10px] p-3" style="background: var(--jy-orange-soft)">
            <div class="text-[11px]" style="color: var(--jy-orange-ink)">{{ i18n.t("codPending") }}</div>
            <div class="num text-[18px] font-extrabold" style="color: var(--jy-orange-ink)">{{ moneyFull(d.cod.pending) }} <span class="text-[11px]">MAD</span></div>
          </div>
        </div>
      </div>

      <!-- Late orders strip -->
      <button
        class="mb-3 flex w-full items-center gap-3 rounded-[14px] p-3.5 text-start"
        style="background: var(--jy-red-tint); border: 1px solid rgba(196,48,28,0.18)"
        @click="router.push('/ops/alerts')"
      >
        <span class="anim-pulse num grid h-8 w-8 shrink-0 place-items-center rounded-full text-[13px] font-extrabold text-white" style="background: var(--jy-red)">{{ d.late }}</span>
        <span class="flex-1">
          <span class="block text-[13px] font-extrabold" style="color: var(--jy-red)">{{ i18n.t("lateTitle") }}</span>
          <span class="block text-[11px]" style="color: var(--jy-text-2)">{{ i18n.t("lateSub") }}</span>
        </span>
        <Icon name="chevron" :size="16" :style="{ color: 'var(--jy-red)', transform: i18n.isAr.value ? 'scaleX(-1)' : 'none' }" />
      </button>

      <!-- Daily report -->
      <div class="card mb-2 p-4">
        <div class="text-[13px] font-extrabold">{{ i18n.t("reportTitle") }}</div>
        <div class="mb-3 mt-0.5 text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("reportSub") }}</div>
        <div class="grid grid-cols-2 gap-2.5">
          <button class="tap flex items-center justify-center gap-1.5 rounded-[10px] text-[12px] font-extrabold text-white" style="background: var(--jy-wa); height: 40px">
            <Icon name="wa" :size="15" color="#fff" />{{ i18n.t("reportWa") }}
          </button>
          <button class="tap flex items-center justify-center gap-1.5 rounded-[10px] text-[12px] font-extrabold" style="background: var(--jy-bg-2); border: 1px solid var(--jy-line); color: var(--jy-ink); height: 40px">
            <Icon name="download" :size="15" style="color: var(--jy-ink)" />{{ i18n.t("reportPdf") }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";
import Icon from "@/components/Icon.vue";
import PeriodTabs from "@/components/PeriodTabs.vue";
import { createResource } from "@/lib/resource";
import { useI18n } from "@/i18n";
import { useDashboard } from "@/composables/useDashboard";
import { n, money, moneyFull, signed } from "@/lib/format";

const i18n = useI18n();
const router = useRouter();
const { period, refreshNonce } = useDashboard();

const res = createResource({ url: "ops_dashboard.api.kpis.home" });
const d = computed(() => res.data || {});

// count-up animation for the hero number
const shownOrdersNum = ref(0);
const shownOrders = computed(() => Number(shownOrdersNum.value || 0).toLocaleString("en-US"));
function countUp(from, to) {
  const start = performance.now();
  const dur = 700;
  function tick(now) {
    const p = Math.min(1, (now - start) / dur);
    const eased = 1 - Math.pow(1 - p, 3);
    shownOrdersNum.value = Math.round(from + (to - from) * eased);
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

async function load() {
  const prev = shownOrdersNum.value;
  await res.fetch({ period: period.value });
  countUp(prev, d.value.orders || 0);
}
function reload() { load(); }

load();
watch(period, () => load());
watch(refreshNonce, () => load());

const deltaPos = computed(() => (d.value.orders_delta_pct || 0) >= 0);
const cmpLabel = computed(() => ({ today: i18n.t("vsYesterday"), d7: i18n.t("vsLastWeek"), d30: i18n.t("vsLastMonth") }[period.value]));
const nowTime = computed(() => new Date().toLocaleTimeString(i18n.isAr.value ? "ar-EG" : "en-US", { hour: "2-digit", minute: "2-digit" }));

// week bars normalized 10–40px, today highlighted orange
const weekBars = computed(() => {
  const week = d.value.week || [];
  const counts = week.map((w) => w.count);
  const min = Math.min(...counts, 0), max = Math.max(...counts, 1);
  const dayLabels = i18n.isAr.value ? ["ح", "ن", "ث", "ع", "خ", "ج", "س"] : ["S", "M", "T", "W", "T", "F", "S"];
  return week.map((w, i) => {
    const dt = new Date(w.date);
    const label = isNaN(dt) ? "" : dayLabels[dt.getDay()];
    const h = max === min ? 25 : 10 + ((w.count - min) / (max - min)) * 30;
    return {
      h: Math.round(h) + "px",
      label,
      color: i === week.length - 1 ? "var(--jy-orange)" : "rgba(255,255,255,0.22)",
      delay: i * 55 + "ms",
    };
  });
});

const funnel = computed(() => {
  const f = d.value.funnel || {};
  const stages = [
    { key: "new", label: i18n.t("fNew"), color: "#b8b8b8", v: f.new },
    { key: "confirmed", label: i18n.t("fConfirmed"), color: "var(--jy-orange)", v: f.confirmed },
    { key: "dispatched", label: i18n.t("fDispatched"), color: "var(--jy-blue)", v: f.dispatched },
    { key: "delivered", label: i18n.t("fDelivered"), color: "var(--jy-green)", v: f.delivered },
  ];
  const mx = stages[0].v || 1;
  return stages.map((s, i) => ({
    ...s, count: s.v || 0,
    w: Math.max(6, Math.round((s.v / mx) * 100)) + "%",
    delay: 120 + i * 90 + "ms",
  }));
});

const rateCards = computed(() => {
  const r = d.value.rates || {};
  const dcol = (v) => (v < 0 ? "var(--jy-red)" : "var(--jy-green)");
  return [
    { key: "conf", label: i18n.t("rConfirmation"), value: (r.confirmation?.value ?? 0) + "%", delta: signed(r.confirmation?.delta) + "%", deltaColor: dcol(r.confirmation?.delta), icon: "check", iconBg: "var(--jy-green-tint)", iconColor: "var(--jy-green)" },
    { key: "deliv", label: i18n.t("rDelivery"), value: (r.delivery?.value ?? 0) + "%", delta: signed(r.delivery?.delta) + "%", deltaColor: dcol(r.delivery?.delta), icon: "pin", iconBg: "var(--jy-orange-soft)", iconColor: "var(--jy-orange-ink)" },
    { key: "aov", label: i18n.t("rAov"), value: n(r.aov?.value ?? 0), delta: signed(r.aov?.delta, 0) + " MAD", deltaColor: dcol(r.aov?.delta), icon: "cash", iconBg: "var(--jy-orange-soft)", iconColor: "var(--jy-orange)" },
    // returns: up is bad
    { key: "ret", label: i18n.t("rReturns"), value: (r.returns?.value ?? 0) + "%", delta: signed(r.returns?.delta) + "%", deltaColor: (r.returns?.delta ?? 0) > 0 ? "var(--jy-red)" : "var(--jy-green)", icon: "ret", iconBg: "var(--jy-red-tint)", iconColor: "var(--jy-red)" },
  ];
});
</script>
