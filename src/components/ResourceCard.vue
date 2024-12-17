<script setup lang="ts">
import { useApiStore } from "@/store";
import { ref, onMounted, onUnmounted, computed } from "vue";
import ResourceLink from "./ResourceLink.vue";

const props = defineProps<{
  uid: string;
}>();
const apiStore = useApiStore();
const thumbnailUrl = ref<string>();
const record = computed(() => apiStore.recordByUid[props.uid]);

onMounted(() => {
  if (!record.value) return;
  apiStore.fetchThumbnail(record.value).then((buf) => {
    const blob = new Blob([buf], { type: "image/webp" });
    thumbnailUrl.value = URL.createObjectURL(blob);
  });
});

onUnmounted(() => {
  if (thumbnailUrl.value) {
    URL.revokeObjectURL(thumbnailUrl.value);
  }
});
</script>

<template>
  <div class="w-[300px] border border-dim rounded overflow-hidden">
    <div class="w-full h-[200px] bg-input" v-loading="!thumbnailUrl">
      <img
        :src="thumbnailUrl"
        alt="Thumbnail"
        class="object-contain w-full h-full"
        v-show="thumbnailUrl"
      />
    </div>

    <div class="h-10 flex items-center p-2">
      <ResourceLink :uid="uid" />
    </div>
  </div>
</template>
