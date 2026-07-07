<template>
  <div>
    <div class="flex rounded-full p-[3px]" style="background: var(--jy-bg-2)">
      <button
        v-for="p in items" :key="p.id"
        class="flex-1 rounded-full py-1.5 text-[12px] font-bold transition"
        :style="p.active ? 'background: var(--jy-surface); color: var(--jy-ink); box-shadow: 0 1px 3px rgba(15,15,15,0.12)' : 'color: var(--jy-mute)'"
        @click="p.go"
      ><span :class="{ num: p.id === 'custom' && isCustom }">{{ p.label }}</span></button>
    </div>

    <!-- Custom range sheet -->
    <Sheet v-model="open">
      <div class="mb-4 text-[15px] font-extrabold">{{ i18n.t("customTitle") }}</div>
      <div class="mb-3 grid grid-cols-2 gap-2.5">
        <label class="block">
          <span class="mb-1 block text-[11px] font-bold" style="color: var(--jy-mute)">{{ i18n.t("fromLabel") }}</span>
          <input
            v-model="from" type="date" :max="today"
            class="num w-full rounded-[10px] px-3 py-2.5 text-[13px] font-bold outline-none"
            style="background: var(--jy-bg-2); color: var(--jy-ink); border: 1px solid var(--jy-line); color-scheme: inherit"
          />
        </label>
        <label class="block">
          <span class="mb-1 block text-[11px] font-bold" style="color: var(--jy-mute)">{{ i18n.t("toLabel") }}</span>
          <input
            v-model="to" type="date" :max="today"
            class="num w-full rounded-[10px] px-3 py-2.5 text-[13px] font-bold outline-none"
            style="background: var(--jy-bg-2); color: var(--jy-ink); border: 1px solid var(--jy-line); color-scheme: inherit"
          />
        </label>
      </div>
      <!-- quick presets -->
      <div class="mb-4 flex flex-wrap gap-2">
        <button
          v-for="q in quicks" :key="q.label"
          class="pill px-3 py-1.5 text-[11px] font-bold"
          style="background: var(--jy-bg-2); color: var(--jy-text-2); border: 1px solid var(--jy-line)"
          @click="q.set"
        >{{ q.label }}</button>
      </div>
      <button
        class="tap w-full rounded-[12px] text-[13px] font-extrabold disabled:opacity-40"
        style="background: var(--jy-orange); color: #1a1a1a; height: 44px"
        :disabled="!from || !to"
        @click="apply"
      >{{ i18n.t("applyBtn") }}</button>
    </Sheet>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import Sheet from "@/components/Sheet.vue";
import { useI18n } from "@/i18n";
import { useDashboard } from "@/composables/useDashboard";

const i18n = useI18n();
const { period, fromDate, toDate, setPeriod, setCustomRange } = useDashboard();

const open = ref(false);
const from = ref(null);
const to = ref(null);

// local-date "YYYY-MM-DD" — never toISOString(), which shifts to UTC and can
// land a day off depending on the timezone
function fmtLocal(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
const today = fmtLocal(new Date());
const isCustom = computed(() => period.value === "custom");

function iso(daysAgo) {
  const d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return fmtLocal(d);
}

// e.g. "1/6–15/6" on the segment once a range is applied (numerals stay LTR)
const rangeLabel = computed(() => {
  if (!isCustom.value || !fromDate.value || !toDate.value) return null;
  const [fy, fm, fd] = fromDate.value.split("-").map(Number);
  const [ty, tm, td] = toDate.value.split("-").map(Number);
  return `${fd}/${fm}–${td}/${tm}`;
});

const items = computed(() => [
  { id: "today", label: i18n.t("today"), active: period.value === "today", go: () => setPeriod("today") },
  { id: "d7", label: i18n.t("d7"), active: period.value === "d7", go: () => setPeriod("d7") },
  { id: "d30", label: i18n.t("d30"), active: period.value === "d30", go: () => setPeriod("d30") },
  {
    id: "custom",
    label: rangeLabel.value || i18n.t("customTab"),
    active: isCustom.value,
    go: () => {
      from.value = fromDate.value || iso(6);
      to.value = toDate.value || today;
      open.value = true;
    },
  },
]);

const quicks = computed(() => [
  { label: i18n.t("qYesterday"), set: () => { from.value = iso(1); to.value = iso(1); } },
  { label: i18n.t("qThisMonth"), set: () => { const d = new Date(); from.value = fmtLocal(new Date(d.getFullYear(), d.getMonth(), 1)); to.value = today; } },
  { label: i18n.t("qLastMonth"), set: () => { const d = new Date(); from.value = fmtLocal(new Date(d.getFullYear(), d.getMonth() - 1, 1)); to.value = fmtLocal(new Date(d.getFullYear(), d.getMonth(), 0)); } },
  { label: i18n.t("qLast90"), set: () => { from.value = iso(89); to.value = today; } },
]);

function apply() {
  setCustomRange(from.value, to.value);
  open.value = false;
}
</script>
