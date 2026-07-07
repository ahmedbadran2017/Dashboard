<template>
  <div class="flex rounded-full p-[3px]" style="background: var(--jy-bg-2)">
    <button
      v-for="p in items" :key="p.id"
      class="flex-1 rounded-full py-1.5 text-[12px] font-bold transition"
      :style="p.id === period ? 'background: var(--jy-surface); color: var(--jy-ink); box-shadow: 0 1px 3px rgba(15,15,15,0.12)' : 'color: var(--jy-mute)'"
      @click="setPeriod(p.id)"
    >{{ p.label }}</button>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "@/i18n";
import { useDashboard } from "@/composables/useDashboard";

const i18n = useI18n();
const { period, setPeriod } = useDashboard();
const items = computed(() => [
  { id: "today", label: i18n.t("today") },
  { id: "d7", label: i18n.t("d7") },
  { id: "d30", label: i18n.t("d30") },
]);
</script>
