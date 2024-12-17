<script lang="ts" setup>
import EpubTocItem from "./EpubTocItem.vue";
import type { NavItem } from "epubjs";

defineProps<{
  toc: Array<NavItem>;
  activeHref: string;
}>();

const emit = defineEmits<{
  (event: "select", href: string): void;
}>();
</script>

<template>
  <nav>
    <ul>
      <EpubTocItem
        v-for="item in toc"
        :key="item.id"
        :item="item"
        :level="1"
        :activeHref="activeHref"
        @select="emit('select', $event)"
      />
    </ul>
  </nav>
</template>
