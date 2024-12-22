<script lang="ts" setup>
import { faAngleDown, faCheck } from "@fortawesome/free-solid-svg-icons";
import { ref, computed } from "vue";

const props = defineProps<{
  records: AnyRecord[];
  multiple?: boolean;
}>();
const emit = defineEmits<{
  (e: "select", uids: string[]): void;
}>();

const isKindDropdownOpen = ref(false);
const selectedKind = ref<string>("all");
const searchText = ref("");
const selectedRecordUids = ref<Set<string>>(new Set());
const kinds = ["all", "video", "image", "book", "note", "file"];

const filteredRecords = computed(() => {
  let result = props.records;

  if (selectedKind.value !== "all") {
    result = result.filter((r) => r.kind === selectedKind.value);
  }

  if (searchText.value) {
    const keywords = searchText.value
      .toLowerCase()
      .split(" ")
      .filter((k) => k);
    result = result.filter((item) =>
      keywords.every(
        (keyword) =>
          item.title.toLowerCase().includes(keyword) ||
          item.description.toLowerCase().includes(keyword),
      ),
    );
  }

  return result;
});

const selectStats = computed(() => {
  return {
    filSel: filteredRecords.value.reduce(
      (sum, record) => sum + Number(selectedRecordUids.value.has(record.uid)),
      0,
    ),
    filTot: filteredRecords.value.length,
    allSel: selectedRecordUids.value.size,
    allTot: props.records.length,
  };
});

const highlightText = (text: string) => {
  if (!searchText.value) return text;
  const keywords = searchText.value
    .toLowerCase()
    .split(" ")
    .filter((k) => k);
  let highlighted = text;
  keywords.forEach((keyword) => {
    const regex = new RegExp(`(${keyword})`, "gi");
    highlighted = highlighted.replace(
      regex,
      '<mark class="bg-yellow-200">$1</mark>',
    );
  });
  return highlighted;
};

const handleRecordClick = (uid: string) => {
  if (!props.multiple) {
    emit("select", [uid]);
  } else {
    if (selectedRecordUids.value.has(uid)) {
      selectedRecordUids.value.delete(uid);
    } else {
      selectedRecordUids.value.add(uid);
    }
  }
};

const toggleSelectAll = () => {
  if (selectStats.value.filSel < selectStats.value.filTot) {
    filteredRecords.value.forEach((r) => selectedRecordUids.value.add(r.uid));
  } else {
    filteredRecords.value.forEach((r) =>
      selectedRecordUids.value.delete(r.uid),
    );
  }
};

const submitSelection = () => {
  emit("select", Array.from(selectedRecordUids.value));
};
</script>

<template>
  <div class="relative accent-green-600 min-h-[400px]">
    <!-- Search Bar -->
    <div class="flex mb-4 border rounded-lg">
      <div class="relative">
        <button
          class="pl-4 py-2 flex items-center gap-2 capitalize"
          @click="isKindDropdownOpen = !isKindDropdownOpen"
        >
          <span>{{ selectedKind }}</span>
          <fa-icon :icon="faAngleDown" />
        </button>

        <!-- Kind Dropdown -->
        <div
          v-if="isKindDropdownOpen"
          class="absolute top-full left-0 mt-1 bg-white border rounded-lg shadow-lg z-10"
        >
          <button
            v-for="kind in kinds"
            :key="kind"
            @click="
              selectedKind = kind;
              isKindDropdownOpen = false;
            "
            class="block w-full px-4 py-2 text-left capitalize hover:bg-gray-100"
            v-text="kind"
          />
        </div>
      </div>

      <input
        type="text"
        v-model="searchText"
        placeholder="Search..."
        class="flex-1 px-4 py-2 outline-none rounded-lg"
      />
    </div>

    <!-- Multiple Select Header -->
    <div v-if="multiple" class="flex items-center gap-4 mb-4">
      <span>
        <input
          type="checkbox"
          :checked="
            selectStats.filSel === selectStats.filTot && selectStats.filSel > 0
          "
          :indeterminate="
            selectStats.filSel > 0 && selectStats.filSel < selectStats.filTot
          "
          @change="toggleSelectAll"
        />
      </span>
      <span v-text="`${selectStats.filSel}/${selectStats.filTot}`" />
      <span v-text="`(${selectStats.allSel}/${selectStats.allTot})`" />
    </div>

    <!-- Records List -->
    <div class="space-y-2">
      <div
        v-for="r in filteredRecords"
        :key="r.uid"
        @click="handleRecordClick(r.uid)"
        class="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
        :class="{ 'bg-blue-50': selectedRecordUids.has(r.uid) }"
      >
        <div class="flex items-center gap-4">
          <input
            v-if="multiple"
            type="checkbox"
            :checked="selectedRecordUids.has(r.uid)"
            @click.stop
            @change="handleRecordClick(r.uid)"
          />
          <div>
            <div class="font-semibold" v-html="highlightText(r.title)"></div>
            <div
              class="text-gray-600"
              v-html="highlightText(r.description)"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Button for Multiple Select -->
    <button
      v-if="multiple"
      @click="submitSelection"
      class="absolute bottom-2 right-2 size-8 bg-green-600 text-white rounded-full flex items-center justify-center shadow-lg hover:opacity-50"
    >
      <fa-icon :icon="faCheck" />
    </button>
  </div>
</template>
