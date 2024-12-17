<script lang="ts" setup>
import "viewerjs/dist/viewer.css";
import Viewer from "viewerjs";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";
import { useApiStore } from "@/store";
import { nextTick, onMounted, onUnmounted, ref, computed } from "vue";
import ViewerHeader from "@/components/ViewerHeader.vue";
import Layout from "@/components/Layout.vue";
import { wAlert, wLoading } from "@/widgets";

const route = useRoute();
const router = useRouter();
const apiStore = useApiStore();

const record = computed(() => apiStore.getRecord(route.params.uid as string));
const url = ref("");
const galleryEl = ref<HTMLElement>();

onMounted(async () => {
  if (!galleryEl.value || !record.value) {
    router.back();
    return;
  }

  try {
    wLoading.open("");

    const buf = await apiStore.fetchFile(record.value);
    const blob = new Blob([buf], { type: record.value.mime_type });

    url.value = URL.createObjectURL(blob);

    await nextTick();
    new Viewer(galleryEl.value!);
  } catch (error) {
    wAlert.open({ kind: "error", message: String(error) });
  } finally {
    wLoading.resolve("ok");
  }
});

onUnmounted(() => {
  if (url.value) URL.revokeObjectURL(url.value);
});
</script>

<template>
  <Layout container v-if="record">
    <template #header="{ float }">
      <ViewerHeader :record="record" :data-float="float" />
    </template>

    <div class="text-center">
      <p ref="galleryEl" class="flex justify-center">
        <img :src="url" class="max-w-full" />
      </p>
      <p class="font-bold">{{ record.title }}</p>
      <p>{{ record.description }}</p>
      <p class="text-sm text-dim">{{ record.creation_time }}</p>
    </div>
  </Layout>
</template>
