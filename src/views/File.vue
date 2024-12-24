<script lang="ts" setup>
import ViewerHeader from "@/components/ViewerHeader.vue";
import Layout from "@/components/Layout.vue";
import { useApiStore } from "@/store";
import { useRoute, useRouter } from "vue-router";
import { computed, onMounted, onUnmounted } from "vue";
import { bytesToString } from "@/store/utils";
import { wAlert, wLoading } from "@/widgets";

const route = useRoute();
const router = useRouter();
const apiStore = useApiStore();

const record = computed(() => apiStore.getRecord(route.params.uid as string));
let url = "";

async function download() {
  if (!record.value) return;

  try {
    wLoading.open("");

    const buf = await apiStore.fetchFile(record.value);
    const blob = new Blob([buf], { type: record.value.mime_type });

    url = URL.createObjectURL(blob);

    const aEl = document.createElement("a");

    aEl.href = url;
    aEl.download = record.value.original_name;
    aEl.click();
  } catch (error) {
    wAlert.open({ kind: "error", message: String(error) });
  } finally {
    wLoading.resolve("ok");
  }
}

onMounted(() => {
  if (!record.value) router.back();
});

onUnmounted(() => {
  if (url) URL.revokeObjectURL(url);
});
</script>

<template>
  <Layout v-if="record">
    <template #header="{ float }">
      <ViewerHeader :record="record" :data-float="float" />
    </template>

    <div class="p-6 text-center space-y-4 break-words">
      <h3 class="font-bold text-2xl">{{ record.title }}</h3>
      <p>{{ record.description }}</p>
      <p class="text-dim">{{ bytesToString(record.size) }}</p>
      <p>
        <button
          class="bg-input rounded p-2 shadow shadow-black border-t border-t-dim hover:bg-dim"
          v-text="'Download'"
          @click="download"
        />
      </p>
    </div>
  </Layout>
</template>
