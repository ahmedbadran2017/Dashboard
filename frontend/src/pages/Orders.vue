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

    <!-- Source chips -->
    <div class="mb-2 flex gap-2 overflow-x-auto pb-1">
      <button
        v-for="s in sourceChips" :key="s.id"
        class="pill flex shrink-0 items-center gap-1.5 whitespace-nowrap px-3 py-1 text-[11px] font-bold"
        :style="s.id === source
          ? 'background: var(--jy-blue-tint); color: var(--jy-blue); border: 1px solid var(--jy-blue)'
          : 'background: var(--jy-surface); color: var(--jy-mute); border: 1px solid var(--jy-line)'"
        @click="source = s.id"
      ><span v-if="s.dot" class="h-[7px] w-[7px] rounded-[2px]" :style="{ background: s.dot }" />{{ s.label }}</button>
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
        <div class="flex items-center gap-1.5">
          <span class="num text-[13px] font-extrabold">{{ o.id }}</span>
          <span v-if="SRC[o.source]" class="h-[7px] w-[7px] shrink-0 rounded-[2px]" :style="{ background: SRC[o.source].color }" :title="SRC[o.source].label" />
        </div>
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
const { periodKey, periodParams, refreshNonce } = useDashboard();

const status = ref("all");
const city = ref("all");
const source = ref("all");
const query = ref("");

// channel colors match the Home sources card
const SRC = {
  shopify: { label: "Shopify", color: "var(--jy-green)" },
  youcan: { label: "YouCan", color: "var(--jy-blue)" },
  landing: { label: "Landing", color: "var(--jy-orange)" },
  agent: { label: "Agent", color: "var(--jy-mute)" },
};

// computed (NOT .value) so the status pill labels re-translate on language toggle;
// the template auto-unwraps ST when it indexes ST[o.status].
const ST = computed(() => ({
  new: { label: i18n.t("sNew"), bg: "var(--jy-bg-2)", fg: "var(--jy-text-2)" },
  conf: { label: i18n.t("sConf"), bg: "var(--jy-orange-soft)", fg: "var(--jy-orange-ink)" },
  disp: { label: i18n.t("sDisp"), bg: "var(--jy-blue-tint)", fg: "var(--jy-blue)" },
  del: { label: i18n.t("sDel"), bg: "var(--jy-green-tint)", fg: "var(--jy-green)" },
  ret: { label: i18n.t("sRet"), bg: "var(--jy-red-tint)", fg: "var(--jy-red)" },
}));

const countsRes = createResource({ url: "ops_dashboard.api.orders.counts" });
const citiesRes = createResource({ url: "ops_dashboard.api.orders.cities" });
const res = createResource({ url: "ops_dashboard.api.orders.list_orders" });
const rows = computed(() => res.data || []);

function loadMeta() {
  countsRes.fetch({ ...periodParams(), source: source.value === "all" ? null : source.value });
  citiesRes.fetch(periodParams());
}
let searchTimer;
function loadList() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    res.fetch({ ...periodParams(), status: status.value, city: city.value, search: query.value,
                source: source.value === "all" ? null : source.value });
  }, query.value ? 220 : 0);
}
loadMeta();
loadList();
watch(periodKey, () => { loadMeta(); loadList(); });
watch(refreshNonce, () => { loadMeta(); loadList(); });
watch([status, city, query], loadList);
watch(source, () => { loadMeta(); loadList(); });

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

const sourceChips = computed(() => [
  { id: "all", label: i18n.t("allSources"), dot: null },
  { id: "shopify", label: i18n.t("srcShopify"), dot: SRC.shopify.color },
  { id: "youcan", label: i18n.t("srcYoucan"), dot: SRC.youcan.color },
  { id: "landing", label: i18n.t("srcLanding"), dot: SRC.landing.color },
  { id: "agent", label: i18n.t("srcAgent"), dot: SRC.agent.color },
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
