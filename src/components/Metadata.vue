<script setup lang="ts">
import { useApiStore } from "@/store";
import { faEdit } from "@fortawesome/free-solid-svg-icons";
import { ref } from "vue";
import MetadataForm from "./MetadataForm.vue";
import { wAlert } from "@/widgets";

const apiStore = useApiStore();

const props = defineProps<{
  record: AnyRecord;
}>();

const mode = ref<"view" | "edit">("view");
const loading = ref(false);

async function saveChanges(metadata: {
  title: string;
  description: string;
  thumbnail?: File;
}) {
  try {
    loading.value = true;
    await apiStore.updateMedia(
      props.record.uid,
      metadata.title !== props.record.title ? metadata.title : undefined,
      metadata.description !== props.record.description
        ? metadata.description
        : undefined,
      metadata.thumbnail,
    );
    await apiStore.fetchRecords();
    mode.value = "view";
  } catch (e) {
    wAlert.open({ kind: "error", message: String(e) });
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div v-loading="loading">
    <div v-show="mode === 'view'">
      <div class="space-y-3 md:space-y-0">
        <div class="md:flex" v-for="(value, key) in record">
          <div
            class="capitalize font-bold md:w-32"
            v-text="key.replace('_', ' ')"
          />
          <div class="break-words">{{ value }}</div>
        </div>
      </div>

      <button class="full-btn mt-2" @click="mode = 'edit'">
        <fa-icon :icon="faEdit" />
        <span>Edit</span>
      </button>
    </div>

    <div v-show="mode === 'edit'">
      <MetadataForm
        :title="record.title"
        :description="record.description"
        @submit="saveChanges"
        @cancel="mode = 'view'"
      />
    </div>
  </div>
</template>
