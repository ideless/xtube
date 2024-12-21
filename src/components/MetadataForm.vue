<script setup lang="ts">
import { faFloppyDisk, faXmark } from "@fortawesome/free-solid-svg-icons";
import FileInput from "./FileInput.vue";
import { ref } from "vue";

const props = defineProps<{
  title: string;
  description: string;
  hideCancel?: boolean;
}>();

const emit = defineEmits<{
  (
    e: "submit",
    metadata: {
      title: string;
      description: string;
      thumbnail?: File;
    },
  ): void;
  (e: "cancel"): void;
}>();

const title = ref(props.title);
const description = ref(props.description);
let thumbnail: File | undefined;
</script>

<template>
  <form
    class="space-y-3 w-full"
    @submit.prevent="
      emit('submit', {
        title: title,
        description: description,
        thumbnail: thumbnail,
      })
    "
  >
    <div>
      <label for="title" aria-required="true">Title</label>
      <input
        v-model="title"
        class="!bg-black/10"
        type="text"
        id="title"
        pattern="^(\S|\S.*\S)$"
      />
    </div>

    <div>
      <label for="description">Description</label>
      <textarea v-model="description" class="!bg-black/10" id="description" />
    </div>

    <div>
      <label>Thumbnail</label>
      <FileInput
        class="!text-green-600"
        @change="(f) => (thumbnail = f)"
        accept="image/*"
      />
    </div>

    <div class="flex gap-2">
      <button
        class="btn bg-black/10 text-black"
        type="button"
        @click="emit('cancel')"
        v-show="!hideCancel"
      >
        <fa-icon :icon="faXmark" />
        <span>Cancel</span>
      </button>
      <button class="btn bg-black text-white" type="submit">
        <fa-icon :icon="faFloppyDisk" />
        <span>Save</span>
      </button>
    </div>
  </form>
</template>

<style scoped>
.btn {
  @apply rounded py-1 space-x-2 w-full hover:opacity-80;
}
</style>
