<script lang="ts" setup>
import ResourceLink from "./ResourceLink.vue";

defineProps<{
  record: NoteRecord;
}>();
</script>

<template>
  <div class="p-4 space-y-2 border border-dim rounded">
    <p>
      <ResourceLink :uid="record.uid" />
    </p>
    <p>{{ record.description }}</p>
    <p class="text-sm text-dim">{{ record.creation_time }}</p>
  </div>
</template>
