<script lang="ts" setup>
import videojs from "video.js";
import "video.js/dist/video-js.css";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";
import { useApiStore } from "@/store";
import { computed, onMounted, ref } from "vue";
import ViewerHeader from "@/components/ViewerHeader.vue";
import Layout from "@/components/Layout.vue";

const route = useRoute();
const router = useRouter();
const apiStore = useApiStore();

const record = computed(() => apiStore.getRecord(route.params.uid as string));

const videoPlayer = ref<HTMLVideoElement>();

onMounted(() => {
  if (!videoPlayer.value || !record.value) {
    router.back();
    return;
  }

  const videoOptions = {
    autoplay: "muted",
    loop: true,
    controls: true,
    playbackRates: [0.5, 1, 1.5, 2],
    sources: [
      {
        src: `/data/${record.value.file}`,
        type: record.value.mime_type,
      },
    ],
    html5: {
      vhs: {
        // https://github.com/videojs/http-streaming
        withCredentials: true,
        cacheEncryptionKeys: true,
      },
    },
  };

  videojs(videoPlayer.value, videoOptions);
});
</script>

<template>
  <Layout container v-if="record">
    <template #header="{ float }">
      <ViewerHeader :record="record" :data-float="float" />
    </template>

    <div class="aspect-video">
      <video
        ref="videoPlayer"
        class="w-full h-full video-js vjs-default-skin vjs-show-big-play-button-on-pause"
      />
    </div>

    <p class="text-lg font-bold">{{ record?.title }}</p>
    <p>{{ record?.description }}</p>
    <p class="text-sm text-dim">{{ record?.creation_time }}</p>
  </Layout>
</template>
