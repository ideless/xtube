<script lang="ts" setup>
defineProps<{
  text?: string | number;
  icon?: any;
  active?: boolean;
  disabled?: boolean;
}>();
</script>

<template>
  <button
    class="flex items-center gap-2 transition-colors duration-300 hover:ring-1 hover:ring-active"
    :class="{
      'text-active': active,
      'opacity-50 cursor-not-allowed': disabled,
    }"
    :disabled="disabled"
  >
    <fa-icon :icon="icon" v-if="icon" />
    <span v-if="text">{{ text }}</span>
  </button>
</template>
