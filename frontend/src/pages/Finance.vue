<template>
  <div class="lg:mx-auto lg:max-w-3xl">
    <h1 class="mb-3 text-[17px] font-extrabold">{{ i18n.t("financeTitle") }}</h1>

    <div v-if="cashRes.loading && !cash.total" class="py-8 text-center text-sm" style="color: var(--jy-mute)">{{ i18n.t("loading") }}</div>

    <div class="lg:grid lg:grid-cols-2 lg:items-start lg:gap-4">
      <!-- Cash position -->
      <div class="card mb-3 p-4 lg:mb-0">
        <div class="mb-1 text-[13px] font-extrabold">{{ i18n.t("cashTitle") }}</div>
        <div class="num mb-3 text-[26px] font-extrabold" style="color: var(--jy-green)">{{ money(cash.total) }} <span class="text-[13px]" style="color: var(--jy-mute)">MAD</span></div>
        <div class="mb-3 grid grid-cols-3 gap-2">
          <div class="rounded-[10px] p-2.5" style="background: var(--jy-bg-2)">
            <div class="text-[10px]" style="color: var(--jy-mute)">{{ i18n.t("inBanks") }}</div>
            <div class="num text-[13px] font-extrabold">{{ money(cash.bank_total) }}</div>
          </div>
          <div class="rounded-[10px] p-2.5" style="background: var(--jy-orange-soft)">
            <div class="text-[10px]" style="color: var(--jy-orange-ink)">{{ i18n.t("atCarriers") }}</div>
            <div class="num text-[13px] font-extrabold" style="color: var(--jy-orange-ink)">{{ money(cash.carrier_float) }}</div>
          </div>
          <div class="rounded-[10px] p-2.5" style="background: var(--jy-bg-2)">
            <div class="text-[10px]" style="color: var(--jy-mute)">{{ i18n.t("onCards") }}</div>
            <div class="num text-[13px] font-extrabold">{{ money(cash.card_total) }}</div>
          </div>
        </div>
        <div v-for="(a, i) in cash.accounts" :key="i" class="flex items-center justify-between border-t py-2 text-[12px]" style="border-color: var(--jy-line)">
          <span class="truncate" style="color: var(--jy-text-2)">{{ a.name }}</span>
          <span class="num shrink-0 font-bold">{{ n(a.bal) }}</span>
        </div>
      </div>

      <!-- Profitability -->
      <div class="card mb-3 p-4 lg:mb-0">
        <div class="mb-3 flex items-baseline justify-between">
          <span class="text-[13px] font-extrabold">{{ i18n.t("profitTitle") }}</span>
          <span class="text-[10px]" style="color: var(--jy-mute)">{{ profit.company }}</span>
        </div>
        <div class="mb-3 flex items-end justify-between">
          <div>
            <div class="text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("netProfit") }}</div>
            <div class="num text-[24px] font-extrabold" style="color: var(--jy-green)">{{ money(profit.net) }}</div>
          </div>
          <div class="text-end">
            <div class="text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("margin") }}</div>
            <div class="num text-[24px] font-extrabold" style="color: var(--jy-orange)">{{ profit.margin }}%</div>
          </div>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-[12px]">
            <span style="color: var(--jy-text-2)">{{ i18n.t("revenue") }}</span>
            <span class="num font-bold">{{ n(profit.revenue) }}</span>
          </div>
          <div class="flex items-center justify-between text-[12px]">
            <span style="color: var(--jy-text-2)">{{ i18n.t("cogs") }}</span>
            <span class="num font-bold" style="color: var(--jy-red)">−{{ n(profit.cogs) }}</span>
          </div>
          <div class="flex items-center justify-between border-t pt-2 text-[12px]" style="border-color: var(--jy-line)">
            <span class="font-bold">{{ i18n.t("grossProfit") }}</span>
            <span class="num font-extrabold">{{ n(profit.gross) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="lg:grid lg:grid-cols-2 lg:items-start lg:gap-4">
      <!-- Supplier payable -->
      <div class="card mb-3 p-4 lg:mb-0">
        <div class="flex items-center gap-3">
          <div class="grid h-10 w-10 shrink-0 place-items-center rounded-[12px]" style="background: var(--jy-red-tint)">
            <Icon name="truck" :size="20" style="color: var(--jy-red)" />
          </div>
          <div class="flex-1">
            <div class="text-[12px]" style="color: var(--jy-mute)">{{ i18n.t("supplierPayable") }}</div>
            <div class="num text-[20px] font-extrabold">{{ money(profit.supplier_payable) }} <span class="text-[11px]" style="color: var(--jy-mute)">MAD</span></div>
          </div>
        </div>
      </div>

      <!-- Top expenses -->
      <div class="card mb-3 p-4 lg:mb-0">
        <div class="mb-3 text-[13px] font-extrabold">{{ i18n.t("topExpenses") }}</div>
        <div v-for="(e, i) in (profit.top_expenses || [])" :key="i" class="mb-2 flex items-center justify-between text-[12px] last:mb-0">
          <span class="truncate" style="color: var(--jy-text-2)">{{ e.name }}</span>
          <span class="num shrink-0 font-bold">{{ n(e.amount) }}</span>
        </div>
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

onMounted(() => { cashRes.fetch(); profitRes.fetch(); });
</script>
