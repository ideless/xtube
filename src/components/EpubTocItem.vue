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
    <div
      class="p-2 data-[active=true]:bg-white/20"
      :data-active="item.href === activeHref && !!activeHref"
    >
      <a
        :class="{
          'cursor-pointer': item.href,
          'cursor-not-allowed text-primary': !item.href,
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
