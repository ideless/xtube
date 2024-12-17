<script lang="ts" setup>
import type { NavItem } from "epubjs";
import EpubTocItem from "./EpubTocItem.vue";

defineProps<{
  item: NavItem;
  level: number;
  activeHref: string;
}>();

const emit = defineEmits<{
  (event: "select", href: string): void;
}>();
</script>

<template>
  <li>
    <div class="p-2">
      <a
        :class="{
          'cursor-pointer underline': item.href,
          'cursor-not-allowed': !item.href,
          'text-active': item.href === activeHref && activeHref,
        }"
        v-text="item.label"
        @click="if (item.href) emit('select', item.href);"
      />
    </div>
    <ul v-if="item.subitems && item.subitems.length" class="pl-2">
      <EpubTocItem
        v-for="subitem in item.subitems"
        :key="subitem.id"
        :item="subitem"
        :level="level + 1"
        :activeHref="activeHref"
        @select="emit('select', $event)"
      />
    </ul>
  </li>
</template>
