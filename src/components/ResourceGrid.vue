<script setup lang="ts">
import { computed } from "vue";
import ResourceCard from "./ResourceCard.vue";

const props = defineProps<{
  uids: string;
}>();

const uids = computed(() => props.uids.split(",").filter(Boolean));
</script>

<template>
  <div
    class="grid justify-items-center gap-6"
    style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))"
  >
    <ResourceCard v-for="uid in uids" :key="uid" :uid="uid" />
  </div>
</template>
