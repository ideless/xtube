<script lang="ts" setup>
import { ref, watch } from "vue";
import { useMediaQuery } from "@vueuse/core"; // For responsive detection
import { wDialog } from ".";

const isMobile = useMediaQuery("(max-width: 640px)");
const isOpen = ref(false);
const isClosing = ref(false);

watch(
  () => wDialog.show,
  (newValue: boolean) => {
    if (newValue) {
      // Open dialog
      isOpen.value = true;
      // Prevent body scrolling when dialog is open
      document.body.style.overflow = "hidden";
    } else {
      // Close dialog
      isClosing.value = true;
      setTimeout(() => {
        isClosing.value = false;
        isOpen.value = false;
        document.body.style.overflow = "";
      }, 300); // Match the transition duration
    }
  },
  { immediate: true },
);
</script>

<template>
  <Teleport to="body">
    <template v-if="isOpen">
      <div
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 transition-opacity duration-300"
        :class="{ 'opacity-0': isClosing }"
        @click.self="wDialog.reject('cancel')"
      >
        <div
          class="bg-white text-black rounded-lg px-6 transition-all duration-300 max-h-[calc(100vh-40px)]"
          :class="{
            // Mobile styles
            'fixed bottom-0 w-full rounded-b-none overflow-auto': isMobile,
            'translate-y-full': isMobile && isClosing,
            // Desktop styles
            'w-[640px] overflow-auto': !isMobile,
            'scale-95 opacity-0': !isMobile && isClosing,
          }"
        >
          <div class="font-bold text-xl py-4 sticky top-0 bg-white z-10">
            {{ wDialog.data.title }}
          </div>
          <div class="pb-4">
            <component
              :is="wDialog.data.content"
              v-bind="wDialog.data.props || {}"
              v-on="wDialog.data.events || {}"
            />
          </div>
        </div>
      </div>
    </template>
  </Teleport>
</template>

<style scoped>
/* Mobile enter animation */
.fixed.bottom-0 {
  animation: slide-up 0.3s ease-out;
}

@keyframes slide-up {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

/* Desktop enter animation */
.w-\[640px\]:not(.scale-95) {
  animation: zoom-in 0.3s ease-out;
}

@keyframes zoom-in {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
