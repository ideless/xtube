<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  records: AnyRecord[];
  multiple?: boolean;
}>();

const emit = defineEmits<{
  (e: "select", records: AnyRecord[]): void;
}>();

const searchText = ref("");

const keywords = computed(() =>
  searchText.value
    .split(" ")
    .filter(Boolean)
    .map((k) => k.toLowerCase()),
);

const filteredRecords = computed(() => {
  const match = (text: string) => keywords.value.every((k) => text.includes(k));

  return props.records.filter(
    (r) =>
      match(r.title.toLowerCase()) ||
      match((r.description || "").toLowerCase()),
  );
});

const selected = ref<Record<string, boolean>>({});

function highlight(text: string) {
  keywords.value.forEach((k) => {
    const escapedK = k.replace(/([.*+?^${}()|[\]\\])/g, (m) => `\\${m}`);
    const regex = new RegExp(escapedK, "i");

    text = text.replace(regex, (m) => `<span class="text-active">${m}</span>`);
  });
  return text;
}

function reset() {
  searchText.value = "";
  selected.value = {};
}

function onClick(record: AnyRecord) {
  if (props.multiple) {
    selected.value[record.uid] = !selected.value[record.uid];
  } else {
    emit("select", [record]);
    reset();
  }
}

function onOK() {
  emit(
    "select",
    props.records.filter((r) => selected.value[r.uid]),
  );
  reset();
}
</script>

<template>
  <div class="w-[600px] max-w-full">
    <div class="flex items-stretch gap-2">
      <input
        class="flex-1 p-2 rounded bg-input"
        type="text"
        placeholder="Search for resources"
        v-model="searchText"
      />
      <button
        class="bg-input rounded p-2 hover:text-active"
        v-show="multiple"
        v-text="'OK'"
        @click="onOK"
      />
    </div>

    <div class="max-h-[50vh] overflow-y-auto text-sm mt-2">
      <button
        class="p-2 block w-full text-left rounded hover:bg-white/10"
        v-for="r in filteredRecords"
        @click="onClick(r)"
      >
        <div :class="{ 'ring-1 ring-active': selected[r.uid] }">
          <div v-html="highlight(r.title)" />
          <div
            class="opacity-50 text-nowrap overflow-hidden text-ellipsis"
            v-html="highlight(r.description)"
          />
        </div>
      </button>
    </div>
  </div>
</template>
