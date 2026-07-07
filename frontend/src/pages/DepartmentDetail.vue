<template>
  <div>
    <button class="mb-3 flex items-center gap-1 text-[13px] font-bold" style="color: var(--jy-blue)" @click="router.back()">
      <Icon name="back" :size="15" :style="{ color: 'var(--jy-blue)', transform: i18n.isAr.value ? 'scaleX(-1)' : 'none' }" />
      {{ i18n.t("back") }}
    </button>

    <div class="mb-4 flex items-center gap-3">
      <div class="grid h-12 w-12 place-items-center rounded-[14px]" :style="{ background: acc.bg }">
        <Icon :name="meta.icon" :size="24" :style="{ color: acc.c }" />
      </div>
      <div>
        <div class="text-[18px] font-extrabold">{{ i18n.L(meta.name) }}</div>
      </div>
    </div>

    <div v-if="res.loading && !d.stats" class="py-8 text-center text-sm" style="color: var(--jy-mute)">{{ i18n.t("loading") }}</div>

    <template v-if="d.stats">
      <!-- 2x2 stats -->
      <div class="mb-3 grid grid-cols-2 gap-2.5">
        <div v-for="(s, i) in d.stats" :key="i" class="card p-3">
          <div class="text-[11px]" style="color: var(--jy-mute)">{{ statLabel(s.l) }}</div>
          <div class="num text-[20px] font-extrabold leading-tight">{{ s.v }}{{ s.unit || "" }}</div>
          <div v-if="s.d !== null && s.d !== undefined" class="num text-[11px] font-bold" :style="{ color: s.d < 0 ? 'var(--jy-red)' : 'var(--jy-green)' }">{{ signed(s.d, 0) }}</div>
        </div>
      </div>

      <!-- 7-day bars -->
      <div class="card mb-3 p-4">
        <div class="mb-3 text-[13px] font-extrabold">{{ i18n.t("weekTrend") }}</div>
        <div class="flex items-end justify-between gap-2" style="height: 64px">
          <div v-for="(b, i) in bars" :key="i" class="flex flex-1 flex-col items-center justify-end gap-1" style="height: 64px">
            <div class="grow-up w-full rounded-t" :style="{ height: b.h, background: b.color, animationDelay: (i * 55) + 'ms' }" />
            <span class="text-[9px]" style="color: var(--jy-mute)">{{ b.label }}</span>
          </div>
        </div>
      </div>

      <!-- Top performers -->
      <div v-if="d.top && d.top.length" class="card p-4">
        <div class="mb-3 text-[13px] font-extrabold">{{ i18n.t("topTeam") }}</div>
        <div v-for="(m, i) in d.top" :key="i" class="mb-3 flex items-center gap-2.5 last:mb-0">
          <div class="grid h-7 w-7 shrink-0 place-items-center rounded-full text-[11px] font-bold" style="background: var(--jy-orange-soft); color: var(--jy-orange-ink)">{{ initials(m.name) }}</div>
          <div class="min-w-0 flex-1">
            <div class="truncate text-[13px] font-bold">{{ m.name }}</div>
            <div class="mt-1 h-[5px] overflow-hidden rounded-full" style="background: var(--jy-bg-2)">
              <div class="h-full rounded-full fill-x" :style="{ width: m.pct + '%', background: 'var(--jy-orange)' }" />
            </div>
          </div>
          <span class="num text-[13px] font-extrabold">{{ n(m.value) }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import Icon from "@/components/Icon.vue";
import { createResource } from "@/lib/resource";
import { useI18n, DEPT_META } from "@/i18n";
import { useDashboard } from "@/composables/useDashboard";
import { n, signed, initials } from "@/lib/format";

const i18n = useI18n();
const route = useRoute();
const router = useRouter();
const { periodKey, periodParams, refreshNonce } = useDashboard();

const deptId = computed(() => route.params.id);
const meta = computed(() => DEPT_META[deptId.value] || { name: [deptId.value, deptId.value], icon: "box", accent: "orange" });
const ACCENT = {
  green: { bg: "var(--jy-green-tint)", c: "var(--jy-green)" },
  orange: { bg: "var(--jy-orange-soft)", c: "var(--jy-orange)" },
  blue: { bg: "var(--jy-blue-tint)", c: "var(--jy-blue)" },
  red: { bg: "var(--jy-red-tint)", c: "var(--jy-red)" },
};
const acc = computed(() => ACCENT[meta.value.accent] || ACCENT.orange);

const res = createResource({ url: "ops_dashboard.api.departments.department_detail" });
const d = computed(() => res.data || {});

function load() { res.fetch({ dept: deptId.value, ...periodParams() }); }
load();
watch(() => route.params.id, load);
watch(periodKey, load);
watch(refreshNonce, load);

const bars = computed(() => {
  const arr = (d.value.bars || []).map((b) => b.count);
  const mx = Math.max(...arr, 1);
  const dayLabels = i18n.isAr.value ? ["ح", "ن", "ث", "ع", "خ", "ج", "س"] : ["S", "M", "T", "W", "T", "F", "S"];
  return (d.value.bars || []).map((b, i) => {
    const dt = new Date(b.date);
    return {
      h: Math.max(8, Math.round((b.count / mx) * 56)) + "px",
      color: i === (d.value.bars.length - 1) ? acc.value.c : "var(--jy-bg-2)",
      label: isNaN(dt) ? "" : dayLabels[dt.getDay()],
    };
  });
});

const STAT_LABELS = {
  confirmed_today: ["اتأكد اليوم", "Confirmed today"],
  awaiting: ["في الانتظار", "Awaiting"],
  rate: ["المعدل", "Rate"],
  total: ["الإجمالي", "Total"],
  delivered_today: ["اتسلم اليوم", "Delivered today"],
  dispatched: ["خرج للشحن", "Dispatched"],
  returned: ["مرتجعات", "Returned"],
  delivered: ["اتسلّم", "Delivered"],
  confirmed: ["اتأكد", "Confirmed"],
  orders: ["أوردرات", "Orders"],
};
function statLabel(k) { return i18n.L(STAT_LABELS[k] || [k, k]); }
</script>
