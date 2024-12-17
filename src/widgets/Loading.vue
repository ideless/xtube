<script setup lang="ts">
import { wLoading } from ".";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";
</script>

<template>
  <div
    class="fixed z-50 inset-0 bg-background flex items-center justify-center gap-2"
    v-show="wLoading.show"
  >
    <fa-icon :icon="faSpinner" class="animate-spin" />
    <span v-show="wLoading.data">{{ wLoading.data }}</span>
  </div>
</template>
