<script lang="ts" setup>
import { faUpload } from "@fortawesome/free-solid-svg-icons";
import { ref } from "vue";

defineProps<{
  accept?: string;
  required?: boolean;
}>();

const emit = defineEmits<{
  (e: "change", file: File | undefined): void;
}>();

const filename = ref("");

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement;

  if (input.files && input.files.length) {
    filename.value = input.files[0].name;
    emit("change", input.files[0]);
  } else {
    filename.value = "";
    emit("change", undefined);
  }
}
</script>

<template>
  <label class="text-center cursor-pointer text-active hover:underline">
    <fa-icon :icon="faUpload" />
    <span class="ml-2">{{ filename || "Choose a file" }}</span>
    <input
      class="hidden"
      type="file"
      multiple="false"
      :accept="accept || '*/*'"
      :required="required"
      @change="onFileChange"
    />
  </label>
</template>
