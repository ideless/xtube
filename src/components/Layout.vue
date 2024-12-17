<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref } from "vue";

const props = defineProps({
  layout: {
    type: String,
    default: "sticky",
    validator(value: string) {
      return ["blog", "sticky"].includes(value);
    },
  },
  showSidebar: {
    type: Boolean,
    default: false,
  },
  sidebarWidth: {
    type: String,
    default: "300px",
  },
  container: {
    type: Boolean,
    default: false,
  },
});

// See https://ryanmulligan.dev/blog/sticky-header-scroll-shadow/

const headerInterscEl = ref<HTMLDivElement>();
const headerFloat = ref(false);
let headerInterscObserver: IntersectionObserver | undefined;

const articleEl = ref<HTMLElement>();
const sidebarFloat = computed(() => {
  if (!articleEl.value) return props.showSidebar;
  else if (articleEl.value.offsetLeft === 0) return props.showSidebar;
  else return false;
});

onMounted(() => {
  if (headerInterscEl.value) {
    headerInterscObserver = new IntersectionObserver(([entry]) => {
      headerFloat.value = !entry.isIntersecting;
    });

    headerInterscObserver.observe(headerInterscEl.value);
  }
});

onUnmounted(() => {
  if (headerInterscObserver) headerInterscObserver.disconnect();
});
</script>

<template>
  <div
    :class="{
      'flex flex-col': layout == 'blog',
    }"
  >
    <div ref="headerInterscEl" data-observer-intercept />

    <header
      :class="{
        // this is bad
        'relative z-20': layout == 'blog',
        'sticky top-0 z-10': layout == 'sticky',
      }"
    >
      <slot name="header" :float="headerFloat" />
    </header>

    <main
      :class="{
        'flex-1 overflow-hidden relative lg:flex lg:items-stretch':
          layout == 'blog',
      }"
    >
      <aside
        class="absolute top-0 bottom-0 left-0 -translate-x-full z-30 transition-transform lg:static lg:translate-x-0"
        :class="{
          'translate-x-0': showSidebar,
        }"
        :style="{
          width: sidebarWidth,
          flex: `0 0 ${sidebarWidth}`,
        }"
        v-if="layout == 'blog'"
      >
        <slot name="sidebar" :float="sidebarFloat" />
      </aside>

      <article
        ref="articleEl"
        :class="{
          'h-full lg:flex-1': layout == 'blog',
          'container mx-auto p-4': container,
        }"
      >
        <slot />
      </article>
    </main>
  </div>
</template>
