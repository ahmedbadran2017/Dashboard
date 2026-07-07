<template>
  <svg
    :width="size" :height="size" viewBox="0 0 24 24" fill="none"
    :stroke="color" :stroke-width="stroke" stroke-linecap="round" stroke-linejoin="round"
    aria-hidden="true"
  >
    <path :d="path" />
  </svg>
</template>

<script setup>
import { computed } from "vue";
import { ICONS } from "@/lib/icons";

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 20 },
  color: { type: String, default: "currentColor" },
  stroke: { type: [Number, String], default: 1.8 },
});
const path = computed(() => ICONS[props.name] || "");
</script>
