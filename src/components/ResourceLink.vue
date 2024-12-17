<script setup lang="ts">
import { faMarkdown } from "@fortawesome/free-brands-svg-icons";
import {
  faVideo,
  faImage,
  faBookOpen,
  faFileCircleQuestion,
} from "@fortawesome/free-solid-svg-icons";
import { useApiStore } from "@/store";
import { computed } from "vue";

const apiStore = useApiStore();

const props = defineProps<{
  uid: string;
}>();

const iconMap = {
  note: faMarkdown,
  video: faVideo,
  image: faImage,
  book: faBookOpen,
  file: faFileCircleQuestion,
};

const record = computed(() => apiStore.recordByUid[props.uid]);
</script>

<template>
  <router-link
    class="space-x-2 overflow-hidden text-ellipsis text-nowrap"
    :to="{ name: record.kind, params: { uid: record.uid } }"
    v-if="record"
  >
    <fa-icon :icon="iconMap[record.kind]" />
    <span v-text="record.title" />
  </router-link>
</template>
