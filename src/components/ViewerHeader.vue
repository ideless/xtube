<script setup lang="ts">
import { useRouter } from "vue-router";
import IconButton from "./IconButton.vue";
import {
  faArrowLeft,
  faCircleInfo,
  faTrash,
} from "@fortawesome/free-solid-svg-icons";
import { wDialog, wConfirm, wAlert, wLoading } from "@/widgets";
import Metadata from "./Metadata.vue";
import { markRaw } from "vue";
import { useApiStore } from "@/store";

const apiStore = useApiStore();

const props = defineProps<{
  record: AnyRecord;
}>();

const router = useRouter();

function showMetadata() {
  wDialog
    .open({
      title: "Metadata",
      content: markRaw(Metadata),
      props,
    })
    .catch(() => {});
}

async function deleteMedia() {
  try {
    await wConfirm.open("Confirm to delete?");
    wLoading.open("");
    await apiStore.deleteMedia([props.record.uid]);
    router.back();
  } catch (error) {
    if (error !== "cancel") {
      wAlert.open({ kind: "error", message: String(error) });
    }
  } finally {
    wLoading.resolve("ok");
  }
}
</script>

<template>
  <div class="p-4 flex items-center justify-center gap-8 widget">
    <IconButton :icon="faArrowLeft" text="Back" @click="router.back()" />
    <IconButton :icon="faCircleInfo" text="Metadata" @click="showMetadata" />
    <IconButton :icon="faTrash" text="Delete" @click="deleteMedia" />
  </div>
</template>
