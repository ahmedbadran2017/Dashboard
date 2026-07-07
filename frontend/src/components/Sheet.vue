<template>
  <teleport to="body">
    <transition name="sheet">
      <div v-if="modelValue" class="fixed inset-0 z-[50]" @click.self="close">
        <div class="absolute inset-0" style="background: rgba(10,10,12,0.45)" @click="close" />
        <div
          class="absolute inset-x-0 bottom-0 mx-auto w-full max-w-[440px]"
          style="background: var(--jy-surface); border-radius: 18px 18px 0 0; box-shadow: 0 -8px 40px rgba(0,0,0,0.25); max-height: 88vh; overflow-y: auto; animation: sheetUp 250ms cubic-bezier(0.2,0,0,1)"
        >
          <div class="sticky top-0 flex justify-center pt-2.5 pb-1" style="background: var(--jy-surface)">
            <span class="block h-1 w-[38px] rounded-full" style="background: var(--jy-mute-2)" />
          </div>
          <div class="px-4 pb-8" style="padding-bottom: max(2rem, env(safe-area-inset-bottom))">
            <slot />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
const props = defineProps({ modelValue: Boolean });
const emit = defineEmits(["update:modelValue"]);
function close() { emit("update:modelValue", false); }
</script>

<style scoped>
.sheet-enter-active, .sheet-leave-active { transition: opacity 150ms ease; }
.sheet-enter-from, .sheet-leave-to { opacity: 0; }
</style>
