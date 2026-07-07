<template>
  <div>
    <h1 class="mb-3 text-[17px] font-extrabold">{{ i18n.t("ordersTitle") }}</h1>

    <!-- Search -->
    <div class="mb-3 flex items-center gap-2 rounded-full px-3.5 py-2.5" style="background: var(--jy-bg-2)">
      <Icon name="search" :size="15" style="color: var(--jy-mute)" />
      <input
        v-model="query" type="search" :placeholder="i18n.t('searchPh')"
        class="w-full bg-transparent text-[13px] outline-none"
        style="color: var(--jy-ink)"
      />
    </div>

    <!-- Status chips -->
    <div class="mb-2 flex gap-2 overflow-x-auto pb-1">
      <button
        v-for="c in statusChips" :key="c.id"
        class="pill flex shrink-0 items-center gap-1 whitespace-nowrap px-3 py-1.5 text-[12px] font-bold"
        :style="c.id === status
          ? 'background: var(--jy-ink); color: var(--jy-surface); border: 1px solid var(--jy-ink)'
          : 'background: var(--jy-surface); color: var(--jy-text-2); border: 1px solid var(--jy-line)'"
        @click="status = c.id"
      >{{ c.label }} <span class="num opacity-70">{{ n(c.count) }}</span></button>
    </div>

    <!-- City chips -->
    <div class="mb-3 flex gap-2 overflow-x-auto pb-1">
      <button
        v-for="c in cityChips" :key="c.id"
        class="pill shrink-0 whitespace-nowrap px-3 py-1 text-[11px] font-semibold"
        :style="c.id === city
          ? 'background: var(--jy-orange-soft); color: var(--jy-orange-ink); border: 1px solid var(--jy-orange)'
          : 'background: transparent; color: var(--jy-mute); border: 1px dashed var(--jy-mute-2)'"
        @click="city = c.id"
      >{{ c.label }}</button>
    </div>

    <div v-if="res.loading && !rows.length" class="py-8 text-center text-sm" style="color: var(--jy-mute)">{{ i18n.t("loading") }}</div>
    <div v-else-if="!rows.length" class="py-8 text-center text-sm" style="color: var(--jy-mute)">—</div>

    <!-- Order rows -->
    <button
      v-for="(o, i) in rows" :key="o.id"
      class="card mb-2 flex w-full items-center gap-3 p-3 text-start anim-stagger"
      :style="{ animationDelay: (Math.min(i, 10) * 40) + 'ms' }"
      @click="openOrder(o)"
    >
      <div class="min-w-0 flex-1">
        <div class="num text-[13px] font-extrabold">{{ o.id }}</div>
        <div class="truncate text-[12px]" style="color: var(--jy-text-2)">{{ o.customer }}</div>
        <div class="truncate text-[10px]" style="color: var(--jy-mute)">{{ o.city }} · <span class="num">{{ o.time }}</span></div>
      </div>
      <div class="flex flex-col items-end gap-1">
        <div><span class="num text-[14px] font-extrabold">{{ n(o.amount) }}</span> <span class="text-[10px]" style="color: var(--jy-mute)">MAD</span></div>
        <span class="pill px-2.5 py-0.5 text-[10px] font-bold" :style="{ background: ST[o.status].bg, color: ST[o.status].fg }">{{ ST[o.status].label }}</span>
      </div>
    </button>

    <!-- Detail sheet -->
    <Sheet v-model="sheetOpen">
      <OrderSheet v-if="current" :order="current" />
    </Sheet>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import Icon from "@/components/Icon.vue";
import Sheet from "@/components/Sheet.vue";
import OrderSheet from "@/components/OrderSheet.vue";
import { createResource } from "@/lib/resource";
import { useI18n } from "@/i18n";
import { useDashboard } from "@/composables/useDashboard";
import { n } from "@/lib/format";

const i18n = useI18n();
const { period, refreshNonce } = useDashboard();

const status = ref("all");
const city = ref("all");
const query = ref("");

const ST = computed(() => ({
  new: { label: i18n.t("sNew"), bg: "var(--jy-bg-2)", fg: "var(--jy-text-2)" },
  conf: { label: i18n.t("sConf"), bg: "var(--jy-orange-soft)", fg: "var(--jy-orange-ink)" },
  disp: { label: i18n.t("sDisp"), bg: "var(--jy-blue-tint)", fg: "var(--jy-blue)" },
  del: { label: i18n.t("sDel"), bg: "var(--jy-green-tint)", fg: "var(--jy-green)" },
  ret: { label: i18n.t("sRet"), bg: "var(--jy-red-tint)", fg: "var(--jy-red)" },
})).value;

const countsRes = createResource({ url: "ops_dashboard.api.orders.counts" });
const citiesRes = createResource({ url: "ops_dashboard.api.orders.cities" });
const res = createResource({ url: "ops_dashboard.api.orders.list_orders" });
const rows = computed(() => res.data || []);

function loadMeta() {
  countsRes.fetch({ period: period.value });
  citiesRes.fetch({ period: period.value });
}
let searchTimer;
function loadList() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    res.fetch({ period: period.value, status: status.value, city: city.value, search: query.value });
  }, query.value ? 220 : 0);
}
loadMeta();
loadList();
watch(period, () => { loadMeta(); loadList(); });
watch(refreshNonce, () => { loadMeta(); loadList(); });
watch([status, city, query], loadList);

const statusChips = computed(() => {
  const c = countsRes.data || {};
  return [
    { id: "all", label: i18n.t("all"), count: c.all || 0 },
    { id: "new", label: i18n.t("sNew"), count: c.new || 0 },
    { id: "conf", label: i18n.t("sConf"), count: c.conf || 0 },
    { id: "disp", label: i18n.t("sDisp"), count: c.disp || 0 },
    { id: "del", label: i18n.t("sDel"), count: c.del || 0 },
    { id: "ret", label: i18n.t("sRet"), count: c.ret || 0 },
  ];
});

const cityChips = computed(() => [
  { id: "all", label: i18n.t("allCities") },
  ...(citiesRes.data || []).map((c) => ({ id: c, label: c })),
]);

// detail sheet
const sheetOpen = ref(false);
const current = ref(null);
const orderRes = createResource({ url: "ops_dashboard.api.orders.get_order" });
async function openOrder(o) {
  current.value = { ...o }; // optimistic
  sheetOpen.value = true;
  const full = await orderRes.fetch({ name: o.id });
  if (full) current.value = full;
}
</script>
