<template>
  <!-- "Needs you today" — the first thing under the headline numbers. A daily
       review starts from what has to be worked, not from charts: each row is a
       queue, and opening it shows the actual orders in it, worst first. -->
  <div class="card mb-3 overflow-hidden lg:[column-span:all]">
    <div class="flex items-center justify-between px-4 pb-2 pt-3.5">
      <span class="text-[13px] font-extrabold">{{ i18n.L(["محتاجك النهاردة", "Needs you today"]) }}</span>
      <button v-if="items.length" class="text-[11px] font-semibold" style="color: var(--jy-mute)" @click="router.push('/ops/alerts')">
        {{ i18n.L(["كل التنبيهات", "All alerts"]) }}
      </button>
    </div>

    <div v-if="res.loading && !res.data" class="px-4 pb-4 text-[12px]" style="color: var(--jy-mute)">
      {{ i18n.t("loading") }}
    </div>

    <!-- Knowing nothing is waiting is worth a line of its own on a daily screen. -->
    <div v-else-if="!items.length" class="mx-4 mb-4 flex items-center gap-2 rounded-[10px] px-3 py-2.5"
         style="background: var(--jy-green-tint)">
      <Icon name="check" :size="15" style="color: var(--jy-green)" />
      <span class="text-[12px] font-semibold" style="color: var(--jy-green)">
        {{ i18n.L(["مفيش حاجة مستنياك دلوقتي", "Nothing is waiting on you right now"]) }}
      </span>
    </div>

    <div v-for="it in items" :key="it.key" class="border-t" style="border-color: var(--jy-line)">
      <button class="flex w-full items-center gap-3 px-4 py-3 text-start" @click="toggle(it.key)">
        <span class="h-2 w-2 shrink-0 rounded-full" :style="{ background: it.dot }" />
        <span class="min-w-0 flex-1">
          <span class="block text-[13px] font-bold">{{ it.title }}</span>
          <span class="block text-[11px]" style="color: var(--jy-mute)">{{ it.sub }}</span>
        </span>
        <span class="text-end">
          <span class="num block text-[15px] font-extrabold" :style="{ color: it.ink }">{{ n(it.count) }}</span>
          <span class="num block text-[10.5px]" style="color: var(--jy-mute)">{{ money(it.value) }} MAD</span>
        </span>
        <Icon name="chevron" :size="15"
              :style="{ color: 'var(--jy-mute)', transition: 'transform 200ms',
                        transform: open === it.key ? 'rotate(90deg)' : (i18n.isAr.value ? 'scaleX(-1)' : 'none') }" />
      </button>

      <div v-if="open === it.key" class="pb-2">
        <button
          v-for="r in it.rows" :key="r.name"
          class="flex w-full items-center gap-3 px-4 py-2 text-start transition hover:bg-[var(--jy-pressed)]"
          @click="openOrder(r, it.key)"
        >
          <span class="num w-[74px] shrink-0 text-[11.5px] font-bold" style="color: var(--jy-text-2)">{{ r.name }}</span>
          <span class="min-w-0 flex-1 truncate text-[12px]">
            {{ r.customer || "—" }}<span v-if="r.city" style="color: var(--jy-mute)"> · {{ r.city }}</span>
            <span v-if="r.carrier_status === 'Delivery Exception'"
                  class="pill ms-1.5 px-1.5 py-px text-[9.5px] font-bold"
                  style="background: var(--jy-red-tint); color: var(--jy-red)">
              {{ i18n.L(["مشكلة عند الكوريير", "Carrier exception"]) }}
            </span>
          </span>
          <span class="num shrink-0 text-[11px] font-semibold" :style="{ color: it.ink }">{{ ageText(r) }}</span>
          <span class="num w-[56px] shrink-0 text-end text-[11.5px] font-bold">{{ n(r.value) }}</span>
        </button>
        <div v-if="it.count > it.rows.length" class="px-4 pt-1 text-[10.5px]" style="color: var(--jy-mute)">
          {{ i18n.L([`+ ${n(it.count - it.rows.length)} تانيين`, `+ ${n(it.count - it.rows.length)} more`]) }}
        </div>
      </div>
    </div>

    <Sheet v-model="sheetOpen">
      <OrderSheet v-if="current" :order="current" />
    </Sheet>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";
import Icon from "@/components/Icon.vue";
import Sheet from "@/components/Sheet.vue";
import OrderSheet from "@/components/OrderSheet.vue";
import { createResource } from "@/lib/resource";
import { useI18n, NEEDS_COPY } from "@/i18n";
import { n, money } from "@/lib/format";
import { useDashboard } from "@/composables/useDashboard";

const i18n = useI18n();
const router = useRouter();

const res = createResource({ url: "ops_dashboard.api.alerts.needs_you", auto: true });

const SEV = {
  red: { dot: "var(--jy-red)", ink: "var(--jy-red)" },
  orange: { dot: "var(--jy-amber)", ink: "var(--jy-amber)" },
};

const items = computed(() =>
  (res.data || []).map((a) => {
    const copy = NEEDS_COPY[a.key] || { title: [a.key, a.key], sub: ["", ""] };
    const sev = SEV[a.severity] || SEV.orange;
    return { ...a, ...sev, title: i18n.L(copy.title), sub: i18n.L(copy.sub), rows: a.rows || [] };
  })
);

const open = ref(null);
function toggle(key) {
  open.value = open.value === key ? null : key;
}

function ageText(r) {
  return r.age_unit === "hours"
    ? i18n.L([`${r.age} س`, `${r.age}h`])
    : i18n.L([`${r.age} يوم`, `${r.age}d`]);
}

// Same open-then-fetch pattern as the Orders page, so the sheet appears
// instantly and fills in when the full order arrives.
const STATUS_GUESS = { overdue_courier: "disp", cod_overdue: "del", not_contacted: "new" };
const sheetOpen = ref(false);
const current = ref(null);
const orderRes = createResource({ url: "ops_dashboard.api.orders.get_order" });
async function openOrder(r, key) {
  current.value = { id: r.name, customer: r.customer, city: r.city, amount: r.value,
                    status: STATUS_GUESS[key] || "new" };
  sheetOpen.value = true;
  const full = await orderRes.fetch({ name: r.name });
  if (full) current.value = full;
}

// Reload with the rest of Home when the header "Refresh" is pressed.
const { refreshNonce } = useDashboard();
watch(refreshNonce, () => res.reload());
</script>
