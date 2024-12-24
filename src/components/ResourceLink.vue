<script setup lang="ts">
import { useApiStore } from "@/store";
import { computed } from "vue";
import { MediaIconMap } from "@/store/icons";

const apiStore = useApiStore();

const props = defineProps<{
  uid: string;
}>();

const record = computed(() => apiStore.recordByUid[props.uid]);
</script>

<template>
  <router-link
    class="space-x-2 overflow-hidden text-ellipsis text-nowrap"
    :to="{ name: record.kind, params: { uid: record.uid } }"
    v-if="record"
  >
    <fa-icon :icon="MediaIconMap[record.kind]" />
    <span v-text="record.title" />
  </router-link>
</template>
