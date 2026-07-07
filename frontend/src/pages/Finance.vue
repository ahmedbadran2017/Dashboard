<template>
  <div class="lg:mx-auto lg:max-w-3xl">
    <h1 class="mb-3 text-[17px] font-extrabold">{{ i18n.t("financeTitle") }}</h1>

    <div v-if="cashRes.loading && !cash.currency" class="py-8 text-center text-sm" style="color: var(--jy-mute)">{{ i18n.t("loading") }}</div>

    <div class="lg:grid lg:grid-cols-2 lg:items-start lg:gap-4">
      <!-- Cash & bank -->
      <div class="card mb-3 p-4 lg:mb-0">
        <div class="mb-1 flex items-baseline justify-between">
          <span class="text-[13px] font-extrabold">{{ i18n.t("cashTitle") }}</span>
          <span class="text-[10px]" style="color: var(--jy-mute)">{{ cash.operating }}</span>
        </div>
        <div class="num mb-1 text-[26px] font-extrabold" :style="{ color: sign(cash.cash_bank) }">
          {{ money(cash.cash_bank) }} <span class="text-[13px]" style="color: var(--jy-mute)">{{ cash.currency }}</span>
        </div>
        <div class="mb-3 text-[11px]" style="color: var(--jy-mute)">
          {{ i18n.t("groupTotal") }}: <span class="num" :style="{ color: sign(cash.total_cash_bank) }">{{ money(cash.total_cash_bank) }}</span>
        </div>
        <div v-for="(c, i) in (cash.companies || [])" :key="i" class="flex items-center justify-between border-t py-2 text-[12px]" style="border-color: var(--jy-line)">
          <span class="truncate" style="color: var(--jy-text-2)">{{ c.company }}</span>
          <span class="flex items-baseline gap-1">
            <span class="num font-bold" :style="{ color: sign(c.cash_bank) }">{{ money(c.cash_bank) }}</span>
            <span class="text-[10px]" style="color: var(--jy-mute)">{{ c.currency }}</span>
          </span>
        </div>
      </div>

      <!-- Profitability YTD -->
      <div class="card mb-3 p-4 lg:mb-0">
        <div class="mb-3 flex items-baseline justify-between">
          <span class="text-[13px] font-extrabold">{{ i18n.t("profitTitle") }}</span>
          <span class="text-[10px]" style="color: var(--jy-mute)">{{ profit.company }}</span>
        </div>
        <div class="mb-3 flex items-end justify-between">
          <div>
            <div class="text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("netProfit") }}</div>
            <div class="num text-[24px] font-extrabold" :style="{ color: sign(profit.net) }">{{ money(profit.net) }}</div>
          </div>
          <div class="text-end">
            <div class="text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("margin") }}</div>
            <div class="num text-[24px] font-extrabold" :style="{ color: sign(profit.margin) }">{{ profit.margin }}%</div>
          </div>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-[12px]">
            <span style="color: var(--jy-text-2)">{{ i18n.t("revenue") }}</span>
            <span class="num font-bold">{{ n(profit.revenue) }}</span>
          </div>
          <div class="flex items-center justify-between text-[12px]">
            <span style="color: var(--jy-text-2)">{{ i18n.t("expenses") }}</span>
            <span class="num font-bold" style="color: var(--jy-red)">−{{ n(profit.expenses) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Supplier payable -->
    <div class="card mb-3 flex items-center gap-3 p-4">
      <div class="grid h-10 w-10 shrink-0 place-items-center rounded-[12px]" style="background: var(--jy-red-tint)">
        <Icon name="truck" :size="20" style="color: var(--jy-red)" />
      </div>
      <div class="flex-1">
        <div class="text-[12px]" style="color: var(--jy-mute)">{{ i18n.t("supplierPayable") }}</div>
        <div class="num text-[20px] font-extrabold">{{ money(profit.supplier_payable) }} <span class="text-[11px]" style="color: var(--jy-mute)">MAD</span></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import Icon from "@/components/Icon.vue";
import { createResource } from "@/lib/resource";
import { useI18n } from "@/i18n";
import { n, money } from "@/lib/format";

const i18n = useI18n();
const cashRes = createResource({ url: "ops_dashboard.api.business.cash" });
const profitRes = createResource({ url: "ops_dashboard.api.business.profit" });
const cash = computed(() => cashRes.data || {});
const profit = computed(() => profitRes.data || {});

// green for positive, red for negative (real GL can be either)
function sign(v) {
  return Number(v || 0) < 0 ? "var(--jy-red)" : "var(--jy-green)";
}

onMounted(() => { cashRes.fetch(); profitRes.fetch(); });
</script>
