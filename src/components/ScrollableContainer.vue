<script lang="ts" setup>
import {
  faAngleDown,
  faAngleUp,
  faLocation,
} from "@fortawesome/free-solid-svg-icons";
import { ref, onMounted } from "vue";

const props = withDefaults(
  defineProps<{
    locationSelector?: string;
    scrollBehavior?: ScrollBehavior;
  }>(),
  {
    scrollBehavior: "smooth",
  },
);

// Refs
const contentRef = ref<HTMLElement>();
const canScrollUp = ref(false);
const canScrollDown = ref(false);

// Methods
function updateScrollButtons() {
  if (!contentRef.value) return;

  const { scrollTop, scrollHeight, clientHeight } = contentRef.value;
  canScrollUp.value = scrollTop > 0;
  canScrollDown.value = scrollTop + clientHeight < scrollHeight;
}

function scrollUp() {
  if (!contentRef.value) return;
  contentRef.value.scrollBy({
    top: -contentRef.value.clientHeight,
    behavior: props.scrollBehavior,
  });
}

function scrollDown() {
  if (!contentRef.value) return;
  contentRef.value.scrollBy({
    top: contentRef.value.clientHeight,
    behavior: props.scrollBehavior,
  });
}

function scrollToTop() {
  if (!contentRef.value) return;
  contentRef.value.scrollTo({
    top: 0,
    behavior: props.scrollBehavior,
  });
}

function scrollToBottom() {
  if (!contentRef.value) return;
  contentRef.value.scrollTo({
    top: contentRef.value.scrollHeight,
    behavior: props.scrollBehavior,
  });
}

function scrollToLocation() {
  if (!contentRef.value || !props.locationSelector) return;

  const el = contentRef.value.querySelector(props.locationSelector);
  if (el) {
    el.scrollIntoView({
      block: "center",
      inline: "nearest",
      behavior: props.scrollBehavior,
    });
  }
}

// Lifecycle hooks
onMounted(() => {
  updateScrollButtons();
});
</script>

<template>
  <div class="relative overflow-hidden">
    <!-- Scrollable content container -->
    <div
      ref="contentRef"
      class="h-full overflow-y-auto"
      @scroll="updateScrollButtons()"
    >
      <slot />
    </div>

    <!-- Scroll buttons -->
    <div class="absolute bottom-4 right-4 flex flex-col gap-2">
      <button
        v-show="canScrollUp"
        @click="scrollUp"
        @dblclick="scrollToTop"
        class="btn"
      >
        <fa-icon :icon="faAngleUp" />
      </button>

      <button v-show="locationSelector" @click="scrollToLocation" class="btn">
        <fa-icon :icon="faLocation" />
      </button>

      <button
        v-show="canScrollDown"
        @click="scrollDown"
        @dblclick="scrollToBottom"
        class="btn"
      >
        <fa-icon :icon="faAngleDown" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.btn {
  @apply w-8 h-8 rounded-full bg-input/50 backdrop-blur text-white flex items-center justify-center hover:bg-input;
}
</style>
