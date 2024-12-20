<script lang="ts" setup>
import FileInput from "@/components/FileInput.vue";
import { useApiStore } from "@/store";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { wAlert } from "@/widgets";
import { useLocalStorage } from "@vueuse/core";

const apiStore = useApiStore();
const router = useRouter();

let file: File | undefined = undefined;
const kindList = ["video", "image", "book", "note", "file"] as const;
const kind = ref<(typeof kindList)[number]>();
const title = ref("");
const description = ref("");
let thumbnail: File | undefined = undefined;
const bitrate = useLocalStorage("upload.form.bitrate", "2000k");
const hls_time = useLocalStorage("upload.form.hls_time", 10);
const resize = useLocalStorage("upload.form.resize", "1920x1080>");
const quality = useLocalStorage("upload.form.quality", 75);
const author = ref("");
const encoding = useLocalStorage("upload.form.encoding", "UTF-8");
const language = useLocalStorage("upload.form.language", "en-US");
const toc_title = useLocalStorage("upload.form.toc_title", "Table of Contents");
const max_ctl = useLocalStorage("upload.form.max_ctl", 50);

const loading = ref(false);

// TODO: generalize to any title
function parseBookTitle() {
  const rawTitle = title.value;

  let m =
    rawTitle.match(/^【(.*)】【(.*)】作者：(.*)$/) ??
    rawTitle.match(/^《(.*)》（(.*)）作者：(.*)$/);

  if (m) {
    title.value = m[1];
    description.value = m[2];
    author.value = m[3];
  }
}

function openFile(f?: File) {
  file = f;

  if (!f) return;

  title.value = f.name.replace(/\.[^.]+$/, "");

  if (f.type.startsWith("video/")) {
    kind.value = "video";
  } else if (f.type.startsWith("image/")) {
    kind.value = "image";
  } else if (f.type === "application/epub+zip" || f.type.startsWith("text/")) {
    kind.value = "book";
    parseBookTitle();
  } else {
    kind.value = "file";
  }
}

function openThumbnail(f?: File) {
  thumbnail = f;
}

function submit() {
  if (!file || !kind.value) return;

  loading.value = true;

  apiStore
    .uploadMedia({
      file,
      kind: kind.value,
      title: title.value,
      description: description.value,
      thumbnail,
      bitrate: bitrate.value,
      hls_time: hls_time.value,
      encoding: encoding.value,
      author: author.value,
      language: language.value,
      toc_title: toc_title.value,
      max_ctl: max_ctl.value,
    })
    .then(() => {
      router.back();
    })
    .catch((e) => {
      wAlert.open({ kind: "error", message: String(e) });
    })
    .finally(() => {
      loading.value = false;
    });
}
</script>

<template>
  <div class="h-screen flex p-4 overflow-auto">
    <div
      class="w-full max-w-[600px] m-auto p-6 rounded shadow-xl shadow-black border-t border-t-dim"
      v-loading="loading"
    >
      <h2 class="font-bold text-lg mb-6">Upload media file</h2>
      <form class="space-y-6" @submit.prevent="submit">
        <div>
          <label aria-required="true">File</label>
          <FileInput @change="openFile" required />
        </div>

        <div>
          <label for="kind" aria-required="true">Kind</label>
          <select id="kind" v-model="kind" required class="capitalize">
            <option :value="k" v-text="k" v-for="k in kindList" />
          </select>
        </div>

        <div>
          <label for="title" aria-required="true">Title</label>
          <input
            id="title"
            type="text"
            v-model="title"
            required
            pattern="^(\S|\S.*\S)$"
          />
        </div>

        <div>
          <label for="description">Description</label>
          <textarea id="description" v-model="description" />
        </div>

        <div>
          <label>Thumbnail</label>
          <FileInput @change="openThumbnail" accept="image/*" />
        </div>

        <div v-show="kind === 'video'">
          <label for="bitrate">Bitrate</label>
          <input id="bitrate" type="text" v-model="bitrate" />
        </div>

        <div v-show="kind === 'video'">
          <label for="hls-time">HLS time (s)</label>
          <input id="hls-time" type="number" min="1" v-model="hls_time" />
        </div>

        <div v-show="kind === 'image'">
          <label for="resize">Resize</label>
          <input id="resize" type="text" v-model="resize" />
        </div>

        <div v-show="kind === 'image'">
          <label for="quality">quality (%)</label>
          <input
            id="quality"
            type="number"
            min="1"
            max="100"
            v-model="quality"
          />
        </div>

        <div v-show="kind === 'book'">
          <label for="author">Author</label>
          <input id="author" type="text" v-model="author" />
        </div>

        <div v-show="kind === 'book'">
          <label for="encoding">Encoding</label>
          <input id="encoding" type="text" v-model="encoding" />
        </div>

        <div v-show="kind === 'book'">
          <label for="language">Language</label>
          <input id="language" type="text" v-model="language" />
        </div>

        <div v-show="kind === 'book'">
          <label for="toc-title">TOC title</label>
          <input id="toc-title" type="text" v-model="toc_title" />
        </div>

        <div v-show="kind === 'book'">
          <label for="max-ctl">Maximum chapter title length</label>
          <input id="max-ctl" type="number" v-model="max_ctl" />
        </div>

        <div class="text-right space-x-4">
          <button
            class="btn"
            type="button"
            v-text="'Cancel'"
            @click="router.back()"
          />
          <button class="btn" type="submit" v-text="'Submit'" />
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.btn {
  @apply px-2 py-1 rounded bg-white/10 border-t border-t-transparent hover:shadow hover:shadow-black hover:border-t-dim;
}
</style>
