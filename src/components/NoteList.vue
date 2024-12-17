<script lang="ts" setup>
import NoteEntry from "./NoteEntry.vue";

defineProps<{
  records: NoteRecord[];
}>();
</script>

<template>
  <div class="space-y-2">
    <NoteEntry v-for="r in records" :key="r.uid" :record="r" />
  </div>
</template>
