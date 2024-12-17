<script lang="ts" setup>
import Layout from "./Layout.vue";
import EpubToc from "./EpubToc.vue";
import IconButton from "./IconButton.vue";
import { faXmark } from "@fortawesome/free-solid-svg-icons";
import type { NavItem } from "epubjs";

defineProps<{
  above: boolean;
  toc: NavItem[];
  secHref: string;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "select", href: string): void;
}>();
</script>

<template>
  <Layout
    class="h-full overflow-x-hidden overflow-y-auto widget break-all"
    :data-float="above"
  >
    <template #header="{ float }">
      <div
        class="flex items-center justify-between p-2"
        :class="{
          'bg-background shadow-md shadow-black': float,
        }"
      >
        <h2>Table of content</h2>
        <IconButton class="lg:hidden" :icon="faXmark" @click="emit('close')" />
      </div>
    </template>

    <EpubToc
      :toc="toc"
      :active-href="secHref"
      @select="emit('select', $event)"
    />
  </Layout>
</template>
