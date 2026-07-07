<template>
  <transition name="banner">
    <div
      v-if="inst.show.value"
      class="fixed inset-x-0 z-40 mx-auto w-full max-w-[440px] px-3"
      :style="{ bottom: 'calc(64px + env(safe-area-inset-bottom) + 14px)' }"
    >
      <div class="card flex items-center gap-3 p-3" style="box-shadow: var(--shadow-2)">
        <img src="/assets/ops_dashboard/icons/icon-64.png" alt="" class="h-10 w-10 shrink-0 rounded-[10px]" />
        <div class="min-w-0 flex-1">
          <div class="text-[13px] font-extrabold">{{ i18n.t("installTitle") }}</div>
          <div v-if="inst.ios.value" class="mt-0.5 text-[11px] leading-snug" style="color: var(--jy-mute)">
            {{ i18n.t("installIos1") }}
            <svg class="inline-block align-[-2px]" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--jy-blue)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M8 7l4-4 4 4M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg>
            {{ i18n.t("installIos2") }}
          </div>
          <div v-else class="mt-0.5 text-[11px]" style="color: var(--jy-mute)">{{ i18n.t("installSub") }}</div>
        </div>
        <button
          v-if="!inst.ios.value"
          class="tap shrink-0 rounded-full px-4 text-[12px] font-extrabold"
          style="background: var(--jy-orange); color: #1a1a1a; height: 36px; min-height: 36px"
          @click="inst.promptInstall"
        >{{ i18n.t("installBtn") }}</button>
        <button class="grid h-7 w-7 shrink-0 place-items-center rounded-full" style="background: var(--jy-bg-2)" @click="inst.dismiss" aria-label="dismiss">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--jy-mute)" stroke-width="2.2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { useInstall } from "@/composables/useInstall";
import { useI18n } from "@/i18n";

const inst = useInstall();
const i18n = useI18n();
</script>

<style scoped>
.banner-enter-active { transition: opacity 300ms ease, transform 300ms cubic-bezier(0.3, 1, 0.3, 1); }
.banner-leave-active { transition: opacity 180ms ease, transform 180ms ease; }
.banner-enter-from, .banner-leave-to { opacity: 0; transform: translateY(14px); }
</style>
