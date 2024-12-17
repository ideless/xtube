<script setup lang="ts">
import { faSpinner } from "@fortawesome/free-solid-svg-icons";

defineProps<{
  fullscreen?: boolean;
}>();
</script>

<template>
  <div
    class="inset-0 bg-background/90 flex items-center justify-center"
    :class="{ 'fixed z-50': fullscreen, absolute: !fullscreen }"
  >
    <fa-icon :icon="faSpinner" class="animate-spin" />
  </div>
</template>
