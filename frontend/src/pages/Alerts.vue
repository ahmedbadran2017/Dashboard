<template>
  <div>
    <h1 class="mb-3 text-[17px] font-extrabold">{{ i18n.t("alertsTitle") }}</h1>

    <div v-if="res.loading && !list.length" class="py-8 text-center text-sm" style="color: var(--jy-mute)">{{ i18n.t("loading") }}</div>
    <div v-else-if="!list.length" class="py-16 text-center text-sm" style="color: var(--jy-mute)">{{ i18n.t("noAlerts") }}</div>

    <div class="lg:grid lg:grid-cols-2 lg:gap-3">
    <div
      v-for="(a, i) in cards" :key="i"
      class="card mb-2.5 flex items-start gap-3 p-3.5 anim-stagger lg:mb-0"
      :style="{ animationDelay: (i * 45) + 'ms', borderInlineStartWidth: '3px', borderInlineStartColor: a.color }"
    >
      <div class="grid h-[30px] w-[30px] shrink-0 place-items-center rounded-full" :style="{ background: a.bg }">
        <Icon :name="a.icon" :size="16" :style="{ color: a.color }" />
      </div>
      <div class="min-w-0 flex-1">
        <div class="text-[13px] font-extrabold leading-snug">{{ a.title }}</div>
        <div class="mt-0.5 text-[11px]" style="color: var(--jy-mute)">{{ a.sub }}</div>
      </div>
      <span class="whitespace-nowrap text-[10px]" style="color: var(--jy-mute)">{{ a.time }}</span>
    </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import Icon from "@/components/Icon.vue";
import { createResource } from "@/lib/resource";
import { useI18n, ALERT_COPY } from "@/i18n";
import { moneyFull, n } from "@/lib/format";

const i18n = useI18n();

const res = createResource({ url: "ops_dashboard.api.alerts.list_alerts", auto: true });
const list = computed(() => res.data || []);

const SEV = {
  red: { color: "var(--jy-red)", bg: "var(--jy-red-tint)" },
  orange: { color: "var(--jy-orange-ink)", bg: "var(--jy-orange-soft)" },
  blue: { color: "var(--jy-blue)", bg: "var(--jy-blue-tint)" },
};
const ICON = {
  stuck: "alert", cod_overdue: "cash", no_confirm_call: "clock",
  return_rate: "ret", low_stock: "info",
};

const cards = computed(() =>
  list.value.map((a) => {
    const copy = ALERT_COPY[a.key] || { title: [a.key, a.key], sub: ["", ""] };
    // {v} is the count for count-based alerts, or the money/percentage value otherwise
    const v = a.count != null ? n(a.count) : (a.key === "cod_overdue" ? moneyFull(a.value) : a.value);
    const sev = SEV[a.severity] || SEV.orange;
    return {
      color: sev.color, bg: sev.bg, icon: ICON[a.key] || "alert",
      title: i18n.L(copy.title, { v }),
      sub: i18n.L(copy.sub),
      time: a.hours_ago != null ? i18n.t("hoursAgo", { n: a.hours_ago }) : i18n.t("today2"),
    };
  })
);
</script>
