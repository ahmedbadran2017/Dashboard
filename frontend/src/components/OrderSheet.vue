<template>
  <div>
    <!-- Header -->
    <div class="mb-4 flex items-start justify-between">
      <div>
        <div class="num text-[17px] font-extrabold">{{ order.id }}</div>
        <div class="text-[13px]" style="color: var(--jy-text-2)">{{ order.customer }}</div>
        <div class="text-[11px]" style="color: var(--jy-mute)">{{ order.city }}<template v-if="order.phone"> · <span class="num">{{ order.phone }}</span></template></div>
      </div>
      <div class="text-end">
        <div><span class="num text-[20px] font-extrabold">{{ n(order.amount) }}</span> <span class="text-[11px]" style="color: var(--jy-mute)">MAD</span></div>
        <span class="pill mt-1 inline-block px-2.5 py-0.5 text-[10px] font-bold" :style="{ background: ST.bg, color: ST.fg }">{{ ST.label }}</span>
      </div>
    </div>

    <!-- Info tiles -->
    <div class="mb-4 grid grid-cols-3 gap-2">
      <div class="rounded-[10px] p-2.5" style="background: var(--jy-bg-2)">
        <div class="text-[10px]" style="color: var(--jy-mute)">{{ i18n.t("confirmAttempts") }}</div>
        <div class="num mt-0.5 text-[12px] font-bold" style="color: var(--jy-green)">{{ order.attempts || 1 }}</div>
      </div>
      <div class="rounded-[10px] p-2.5" style="background: var(--jy-bg-2)">
        <div class="text-[10px]" style="color: var(--jy-mute)">{{ i18n.t("items") }}</div>
        <div class="num mt-0.5 text-[12px] font-bold">{{ order.items_count || 0 }} {{ i18n.t("itemsN") }}</div>
      </div>
      <div class="rounded-[10px] p-2.5" style="background: var(--jy-bg-2)">
        <div class="text-[10px]" style="color: var(--jy-mute)">{{ i18n.t("courier") }}</div>
        <div class="mt-0.5 truncate text-[12px] font-bold">{{ order.courier || "—" }}</div>
      </div>
    </div>

    <!-- Timeline -->
    <div class="mb-4">
      <div v-for="(s, i) in steps" :key="i" class="flex gap-3">
        <div class="flex flex-col items-center">
          <span class="grid h-3 w-3 place-items-center rounded-full" :style="{ background: s.done ? 'var(--jy-green)' : 'var(--jy-surface)', border: '2px solid ' + (s.done ? 'var(--jy-green)' : 'var(--jy-mute-2)') }" />
          <span v-if="i < steps.length - 1" class="w-0.5 flex-1" :style="{ background: s.lineDone ? 'var(--jy-green)' : 'var(--jy-bg-2)', minHeight: '26px' }" />
        </div>
        <div class="pb-3">
          <div class="text-[13px] font-bold" :style="{ color: s.done ? 'var(--jy-ink)' : 'var(--jy-mute-2)' }">{{ s.label }}</div>
          <div class="text-[11px]" style="color: var(--jy-mute)">{{ s.time }}</div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="grid grid-cols-2 gap-2.5">
      <a :href="waLink" target="_blank" class="tap flex items-center justify-center gap-1.5 rounded-[12px] text-[13px] font-extrabold text-white" style="background: var(--jy-wa); height: 44px">
        <Icon name="wa" :size="16" color="#fff" />{{ i18n.t("waCustomer") }}
      </a>
      <a :href="order.tracking_url || '#'" :target="order.tracking_url ? '_blank' : '_self'" class="tap flex items-center justify-center gap-1.5 rounded-[12px] text-[13px] font-extrabold" style="background: var(--jy-bg-2); border: 1px solid var(--jy-line); color: var(--jy-ink); height: 44px">
        <Icon name="truck" :size="16" style="color: var(--jy-ink)" />{{ i18n.t("trackShipment") }}
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import Icon from "@/components/Icon.vue";
import { useI18n } from "@/i18n";
import { n } from "@/lib/format";

const props = defineProps({ order: { type: Object, required: true } });
const i18n = useI18n();

const STATUS = computed(() => ({
  new: { label: i18n.t("sNew"), bg: "var(--jy-bg-2)", fg: "var(--jy-text-2)" },
  conf: { label: i18n.t("sConf"), bg: "var(--jy-orange-soft)", fg: "var(--jy-orange-ink)" },
  disp: { label: i18n.t("sDisp"), bg: "var(--jy-blue-tint)", fg: "var(--jy-blue)" },
  del: { label: i18n.t("sDel"), bg: "var(--jy-green-tint)", fg: "var(--jy-green)" },
  ret: { label: i18n.t("sRet"), bg: "var(--jy-red-tint)", fg: "var(--jy-red)" },
}));
const ST = computed(() => STATUS.value[props.order.status] || STATUS.value.new);

const steps = computed(() => {
  const done = props.order.step_done || 1;
  const defs = [
    { label: i18n.t("tlReceived"), time: props.order.created_at },
    { label: i18n.t("tlConfirmed"), time: "" },
    { label: i18n.t("tlDispatched") + (props.order.courier ? ` · ${props.order.courier}` : ""), time: props.order.shipped_at },
    { label: i18n.t("tlDelivered"), time: props.order.delivered_at },
  ];
  return defs.map((s, i) => ({
    label: s.label,
    time: i < done ? (fmtTime(s.time) || "✓") : i18n.t("pending"),
    done: i < done,
    lineDone: i < done - 1,
  }));
});

function fmtTime(t) {
  if (!t) return "";
  const d = new Date(t);
  if (isNaN(d)) return "";
  return d.toLocaleString(i18n.isAr.value ? "ar-EG" : "en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
}

const waLink = computed(() => {
  const phone = String(props.order.phone || "").replace(/[^\d]/g, "");
  return phone ? `https://wa.me/${phone}` : "#";
});
</script>
