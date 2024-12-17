<script lang="ts" setup>
import { ref } from "vue";
import { useApiStore } from "@/store";
import { useRouter } from "vue-router";
import { faPhotoFilm, faPlus } from "@fortawesome/free-solid-svg-icons";
import { faMarkdown } from "@fortawesome/free-brands-svg-icons";
import ResourceGrid from "@/components/ResourceGrid.vue";
import IconButton from "@/components/IconButton.vue";
import NoteList from "@/components/NoteList.vue";
import Layout from "@/components/Layout.vue";

const apiStore = useApiStore();
const router = useRouter();
const activeTab = ref<"notes" | "resources">("notes");
</script>

<template>
  <Layout container>
    <template #header="{ float }">
      <div class="flex justify-center gap-16 p-4 widget" :data-float="float">
        <IconButton
          :icon="faMarkdown"
          text="Notes"
          :active="activeTab === 'notes'"
          @click="activeTab = 'notes'"
        />
        <IconButton
          :icon="faPhotoFilm"
          text="Resources"
          :active="activeTab === 'resources'"
          @click="activeTab = 'resources'"
        />
      </div>
    </template>

    <NoteList
      v-if="activeTab === 'notes'"
      :records="apiStore.records.filter((r) => r.kind === 'note')"
    />

    <ResourceGrid
      v-if="activeTab === 'resources'"
      :uids="
        apiStore.records
          .filter((r) => r.kind !== 'note')
          .map((r) => r.uid)
          .join(',')
      "
    />

    <button
      class="float-btn"
      @click="router.push({ name: activeTab === 'notes' ? 'edit' : 'upload' })"
    >
      <fa-icon :icon="faPlus" />
    </button>
  </Layout>
</template>

<style scoped>
.tab {
  @apply text-lg cursor-pointer space-x-2 hover:text-active;
}
</style>
