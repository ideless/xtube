<script setup lang="ts">
import { watch } from "vue";

import { wAlert } from ".";
import Modal from "./Modal.vue";
import { ref } from "vue";
import NamedTransition from "@/components/NamedTransition.vue";

const DURATION = 3000;
const width = ref("100%");
let timer: NodeJS.Timeout | null = null;

watch(
  () => wAlert.show,
  (show) => {
    if (timer) {
      clearTimeout(timer);
    }

    if (show) {
      timer = setTimeout(() => {
        wAlert.resolve("closed");
      }, DURATION);

      width.value = "100%";

      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          width.value = "0%";
        });
      });
    }
  },
);
</script>

<template>
  <Modal class="flex items-end justify-center p-2" :show="wAlert.show">
    <NamedTransition name="bounce">
      <div
        class="shadow-md pt-2 pb-3 px-4 rounded transition-transform max-w-full text-wrap break-words text-white relative"
        :class="{
          'bg-gray-700': wAlert.data.kind === 'info',
          'bg-red-900': wAlert.data.kind === 'error',
          'bg-green-900': wAlert.data.kind === 'success',
        }"
        v-if="wAlert.data"
        v-show="wAlert.show"
      >
        <span>{{ wAlert.data.message }}</span>

        <button
          class="text-sky-300 hover:underline ml-4"
          @click="wAlert.resolve('closed')"
          v-text="'OK'"
        />

        <div
          class="absolute bottom-0 left-0 bg-white/30 h-1 transition-all ease-linear"
          :style="{
            'transition-duration': `${DURATION}ms`,
            width,
          }"
          v-show="wAlert.show"
        />
      </div>
    </NamedTransition>
  </Modal>
</template>
