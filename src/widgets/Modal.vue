<script setup lang="ts">
defineProps<{
  show: boolean;
}>();
</script>

<template>
  <div
    class="fixed inset-0 z-50"
    :class="{
      'pointer-events-none': !show,
    }"
  >
    <slot />
  </div>
</template>
