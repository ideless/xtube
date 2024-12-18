<script lang="ts" setup>
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";
import { useApiStore } from "@/store";
import { onMounted, onUnmounted, ref, computed } from "vue";
import { wAlert, wLoading } from "@/widgets";
import ViewerHeader from "@/components/ViewerHeader.vue";
import Layout from "@/components/Layout.vue";
import BookSidebar from "@/components/BookSidebar.vue";
import BookControls from "@/components/BookControls.vue";
import ScrollableContainer from "@/components/ScrollableContainer.vue";
import type { Book, Rendition, NavItem, Location } from "epubjs";
import type Section from "epubjs/types/section";
import ePub from "epubjs";

const route = useRoute();
const router = useRouter();
const apiStore = useApiStore();

const record = computed(() => apiStore.getRecord(route.params.uid as string));

const viewerEl = ref<HTMLDivElement>();

const epub: {
  book?: Book;
  rendition?: Rendition;
} = {};
const NSTOPS = 1000;

const toc = ref<Array<NavItem>>([]);
const showToc = ref(false);
const secHref = ref("");
const secTitle = ref("");
const hasPrev = ref(false);
const percentage = ref(0);
const hasNext = ref(false);
const showHeader = ref(true);

function setPercentage(value: number) {
  if (!epub.book || !epub.rendition) return;

  const cfi = epub.book.locations.cfiFromPercentage(value);
  epub.rendition.display(cfi);
}

onMounted(async () => {
  if (!viewerEl.value || !record.value) {
    router.back();
    return;
  }

  try {
    wLoading.open("");

    const buf = await apiStore.fetchFile(record.value);

    // epub
    epub.book = ePub(buf);
    epub.rendition = epub.book.renderTo(viewerEl.value, {
      flow: "scrolled-doc",
      width: "100%",
    });

    // theme
    const style = window.getComputedStyle(viewerEl.value);
    epub.rendition.themes.override("color", style.color);
    epub.rendition.themes.override("background", "transparent");

    // locations (do not await)
    epub.book.ready.then(() => epub.book!.locations.generate(NSTOPS));

    // reactive data
    toc.value = (await epub.book.loaded.navigation).toc;
    epub.rendition.on("rendered", (section: Section) => {
      secHref.value = section.href;
      secTitle.value = epub.book?.navigation.get(section.href)?.label || "";
      hasPrev.value = !!section.prev();
      hasNext.value = !!section.next();
      const location = epub.rendition!.currentLocation() as any as Location;
      percentage.value = epub.book!.locations.percentageFromCfi(
        location.start.cfi,
      );
    });

    // display
    await epub.rendition.display();
  } catch (error) {
    wAlert.open({ kind: "error", message: String(error) });
  } finally {
    wLoading.resolve("ok");
  }
});

onUnmounted(() => {
  epub.rendition?.destroy();
  epub.book?.destroy();
});
</script>

<template>
  <Layout class="h-screen" layout="blog" :show-sidebar="showToc" v-if="record">
    <template #header>
      <ViewerHeader :record="record" v-show="showHeader" />
    </template>

    <template #sidebar="{ float }">
      <BookSidebar
        :above="float"
        :toc="toc"
        :sec-href="secHref"
        @close="showToc = false"
        @select="epub.rendition?.display($event)"
      />
    </template>

    <ScrollableContainer class="h-full">
      <Layout>
        <template #header="{ float }">
          <BookControls
            :float="float"
            :sec-title="secTitle"
            :has-prev="hasPrev"
            :has-next="hasNext"
            :percentage="percentage"
            :nstops="NSTOPS"
            @toc="showToc = true"
            @prev="epub.rendition?.prev()"
            @next="epub.rendition?.next()"
            @toggle-fullscreen="showHeader = !showHeader"
            @percentage="setPercentage"
          />
        </template>

        <div class="my-2" ref="viewerEl" />
        <div class="h-8" />
      </Layout>
    </ScrollableContainer>
  </Layout>
</template>

<style>
.epub-container {
  overflow: hidden !important;
}

.btn {
  @apply size-8 hover:bg-white/10;
}
</style>
