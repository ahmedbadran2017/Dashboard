<template>
  <div>
    <h1 class="mb-3 text-[17px] font-extrabold">{{ i18n.t("teamTitle") }}</h1>
    <PeriodTabs class="mb-3" />

    <div v-if="res.loading && !sections.length" class="py-8 text-center text-sm" style="color: var(--jy-mute)">{{ i18n.t("loading") }}</div>

    <div
      v-for="(sec, si) in sections" :key="sec.id"
      class="card mb-3 p-4 anim-stagger" :style="{ animationDelay: (si * 90) + 'ms' }"
    >
      <div class="mb-3 flex items-center justify-between">
        <span class="text-[13px] font-extrabold">{{ sectionName(sec.id) }}</span>
        <span class="text-[11px]" style="color: var(--jy-mute)">{{ metricLabel(sec.metric) }}</span>
      </div>

      <template v-if="sec.members && sec.members.length">
        <div v-for="m in sec.members" :key="m.rank" class="mb-3 flex items-center gap-2.5 last:mb-0">
          <span class="num w-4 text-[12px] font-extrabold" :style="{ color: m.rank === 1 ? 'var(--jy-orange)' : 'var(--jy-mute-2)' }">{{ m.rank }}</span>
          <div class="grid h-7 w-7 shrink-0 place-items-center rounded-full text-[11px] font-bold" style="background: var(--jy-orange-soft); color: var(--jy-orange-ink)">{{ m.initials || initials(m.name) }}</div>
          <div class="min-w-0 flex-1">
            <div class="truncate text-[13px] font-bold">{{ m.name }}</div>
            <div class="mt-1 h-[5px] overflow-hidden rounded-full" style="background: var(--jy-bg-2)">
              <div class="h-full rounded-full fill-x" :style="{ width: m.pct + '%', background: m.rank === 1 ? 'var(--jy-orange)' : 'var(--jy-mute-2)' }" />
            </div>
          </div>
          <div class="text-end">
            <div class="num text-[13px] font-extrabold">{{ n(m.value) }}</div>
            <div class="num text-[10px]" style="color: var(--jy-mute)">{{ m.sub }}</div>
          </div>
        </div>
      </template>

      <div v-else class="flex items-center gap-2 rounded-[10px] p-3" style="background: var(--jy-bg-2)">
        <Icon name="info" :size="16" style="color: var(--jy-mute)" />
        <div>
          <div class="text-[12px] font-bold">{{ i18n.t("needsSource") }}</div>
          <div class="text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("needsSourceSub") }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from "vue";
import Icon from "@/components/Icon.vue";
import PeriodTabs from "@/components/PeriodTabs.vue";
import { createResource } from "@/lib/resource";
import { useI18n } from "@/i18n";
import { useDashboard } from "@/composables/useDashboard";
import { n, initials } from "@/lib/format";

const i18n = useI18n();
const { period, refreshNonce } = useDashboard();

const res = createResource({ url: "ops_dashboard.api.team.sections" });
const sections = computed(() => res.data || []);

function load() { res.fetch({ period: period.value }); }
load();
watch(period, load);
watch(refreshNonce, load);

function sectionName(id) {
  return i18n.t({ conf: "teamConf", wh: "teamWh", ret: "teamRet" }[id] || "teamConf");
}
function metricLabel(m) {
  return i18n.t({ confirmed: "mConfirmed", picked: "mPicked", closed: "mClosed" }[m] || "mConfirmed");
}
</script>
