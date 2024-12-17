<script lang="ts" setup>
import { parse } from "@/store/note";
import { computed, defineComponent, onMounted, shallowRef } from "vue";
import type { Component } from "vue";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";
import { useApiStore } from "@/store";
import ResourceLink from "@/components/ResourceLink.vue";
import ResourceGrid from "@/components/ResourceGrid.vue";
import ViewerHeader from "@/components/ViewerHeader.vue";
import Layout from "@/components/Layout.vue";
import { wAlert, wLoading } from "@/widgets";
import { faPen } from "@fortawesome/free-solid-svg-icons";

const route = useRoute();
const router = useRouter();
const apiStore = useApiStore();

const record = computed(() => apiStore.getRecord(route.params.uid as string));
const mdComponent = shallowRef<Component>();

function editNote() {
  router.push({ name: "edit", params: { uid: record.value?.uid } });
}

onMounted(async () => {
  if (!record.value) {
    router.back();
    return;
  }

  try {
    wLoading.open("");

    const buf = await apiStore.fetchFile(record.value);
    const note = new TextDecoder().decode(buf);
    const html = parse(note);
    mdComponent.value = defineComponent({
      components: {
        ResourceLink,
        ResourceGrid,
      },
      template: `<div class="md">${html}</div>`,
    });
  } catch (e) {
    wAlert.open({ kind: "error", message: String(e) });
  } finally {
    wLoading.resolve("ok");
  }
});
</script>

<template>
  <Layout container v-if="record">
    <template #header="{ float }">
      <ViewerHeader :record="record" :data-float="float" />
    </template>

    <component :is="mdComponent" />

    <button class="float-btn" @click="editNote">
      <fa-icon :icon="faPen" />
    </button>
  </Layout>
</template>

<style>
.md {
  @apply space-y-4 leading-loose;
}

.md h1,
.md h2,
.md h3 {
  @apply font-bold;
}

.md h1 {
  @apply text-2xl;
}

.md h2 {
  @apply text-xl;
}

.md h3 {
  @apply text-lg;
}

.md ul,
.md ol {
  @apply list-inside pl-4;
}

.md ul {
  @apply list-disc;
}

.md ol {
  @apply list-decimal;
}

.md a {
  @apply text-active hover:underline;
}

.md blockquote {
  @apply border-l-4 pl-4;
}

.md pre {
  @apply p-4 bg-white/10;
}

.md table {
  @apply w-full;
}

.md thead {
  @apply border-b-2 border-dim;
}

.md tr + tr {
  @apply border-t border-dim;
}

.md th,
.md td {
  @apply text-left;
}
</style>
