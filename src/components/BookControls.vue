<script setup lang="ts">
import { ref } from "vue";
import IconButton from "./IconButton.vue";
import NamedTransition from "./NamedTransition.vue";
import {
  faAnglesLeft,
  faAnglesRight,
  faBars,
  faExpand,
} from "@fortawesome/free-solid-svg-icons";

defineProps<{
  float: boolean;
  secTitle: string;
  hasPrev: boolean;
  hasNext: boolean;
  percentage: number;
  nstops: number;
}>();

const emit = defineEmits<{
  (e: "toc"): void;
  (e: "prev"): void;
  (e: "next"): void;
  (e: "toggleFullscreen"): void;
  (e: "percentage", percentage: number): void;
}>();

const showPercentageInput = ref(false);
</script>

<template>
  <div
    class="p-2 flex items-center gap-2 relative bg-background"
    :class="{ 'shadow-md shadow-black': float }"
  >
    <IconButton class="lg:hidden" :icon="faBars" @click="emit('toc')" />
    <span class="flex-1 text-dim" v-text="secTitle" />
    <IconButton
      :icon="faAnglesLeft"
      @click="emit('prev')"
      :disabled="!hasPrev"
    />
    <IconButton
      :text="Math.round(percentage * 100) + '%'"
      @click="showPercentageInput = !showPercentageInput"
    />
    <IconButton
      :icon="faAnglesRight"
      @click="emit('next')"
      :disabled="!hasNext"
    />
    <IconButton :icon="faExpand" @click="emit('toggleFullscreen')" />
    <NamedTransition name="bounce">
      <div
        class="absolute p-2 top-full right-0 w-80 max-w-full"
        v-show="showPercentageInput"
      >
        <div class="rounded p-2 widget" data-float="true">
          <input
            class="w-full block"
            type="range"
            :value="Math.round(percentage * nstops)"
            :max="nstops"
            @change="emit('percentage', ($event.target as any).value / nstops)"
          />
        </div>
      </div>
    </NamedTransition>
  </div>
</template>
