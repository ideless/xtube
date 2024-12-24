<script setup lang="ts">
import EasyMDE from "easymde";
import "easymde/dist/easymde.min.css";
import "@/assets/fontello/fontello.css";
import { onMounted, ref, markRaw } from "vue";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";
import { useApiStore } from "@/store";
import { wAlert, wConfirm, wDialog, wLoading } from "@/widgets";
import MetadataForm from "@/components/MetadataForm.vue";
import ResourceSelect from "@/components/ResourceSelect.vue";

const route = useRoute();
const router = useRouter();
const apiStore = useApiStore();

const uid = route.params.uid as string;

const textareaEl = ref<HTMLTextAreaElement>();

async function saveAndQuit(note: string) {
  try {
    await wConfirm.open("Save?");
    if (uid) {
      await apiStore.updateNote(uid, note);
    } else {
      const metadata = await wDialog.open({
        title: "Metadata",
        content: markRaw(MetadataForm),
        props: { title: "", description: "", hideCancel: true },
        events: {
          submit: (metadata: any) => wDialog.resolve(metadata),
        },
      });
      await apiStore.createNote(
        metadata.title,
        note,
        metadata.description,
        metadata.thumbnail,
      );
    }
    router.back();
  } catch (e) {
    if (e !== "cancel") {
      wAlert.open({ kind: "error", message: String(e) });
    } else {
      router.back();
    }
  }
}

function selectResources(multiple: boolean) {
  return wDialog.open({
    title: "Select resources",
    content: markRaw(ResourceSelect),
    props: {
      records: apiStore.records,
      multiple,
    },
    events: {
      select: (records: any) => wDialog.resolve(records),
    },
  });
}

function mountEditor(el: HTMLTextAreaElement, initialValue: string) {
  new EasyMDE({
    autoDownloadFontAwesome: false,
    element: el,
    spellChecker: false,
    maxHeight: "50vh",
    initialValue,
    previewClass: "md",
    toolbar: [
      {
        name: "quit",
        action: (editor) => saveAndQuit(editor.value()),
        className: "fa fa-arrow-left",
        title: "Quit",
      },
      "|",
      "bold",
      "italic",
      "strikethrough",
      "heading",
      "code",
      "table",
      "|",
      "link",
      "image",
      {
        name: "resource-link",
        action: (editor) => {
          selectResources(false)
            .then((uids: string[]) => {
              const uid = uids[0];
              editor.codemirror.replaceSelection(`[[${uid}]]`);
              editor.codemirror.focus();
            })
            .catch(() => {});
        },
        className: "fa fa-unlink",
        title: "Resource Link",
      },
      {
        name: "resource-grid",
        action: (editor) => {
          selectResources(true)
            .then((uids: string[]) => {
              const joined = uids.join(",");
              editor.codemirror.replaceSelection(`![[${joined}]]`);
              editor.codemirror.focus();
            })
            .catch(() => {});
        },
        className: "fa fa-th",
        title: "Resource Grid",
      },
      "|",
      "preview",
      "side-by-side",
      "fullscreen",
    ],
  });
}

onMounted(async () => {
  if (!textareaEl.value || !apiStore.loggedIn) {
    router.back();
    return;
  }

  try {
    wLoading.open("");

    if (uid) {
      const record = apiStore.getRecord(uid);

      if (!record) {
        router.back();
        return;
      }

      const buf = await apiStore.fetchFile(record);
      const note = new TextDecoder().decode(buf);

      mountEditor(textareaEl.value, note);
    } else {
      mountEditor(textareaEl.value, "");
    }
  } catch (e) {
    wAlert.open({ kind: "error", message: String(e) });
  } finally {
    wLoading.resolve("ok");
  }
});
</script>

<template>
  <div class="h-screen overflow-hidden p-6">
    <textarea ref="textareaEl" />
  </div>
</template>

<style>
.EasyMDEContainer {
  @apply w-full h-full flex flex-col bg-background text-primary shadow-md shadow-black border-t border-dim rounded overflow-hidden;
}

.EasyMDEContainer .editor-toolbar {
  @apply border-none bg-background;
}

.EasyMDEContainer .editor-toolbar.fullscreen {
  @apply whitespace-nowrap overflow-x-auto overflow-y-hidden;
}

.EasyMDEContainer button {
  @apply border-none hover:!bg-white/10;
}

.EasyMDEContainer button.active {
  @apply bg-transparent text-active;
}

.EasyMDEContainer .separator {
  @apply !border-l-dim !border-r-dim;
}

.EasyMDEContainer .CodeMirror {
  @apply flex-1 bg-neutral-700 text-current border-none font-mono;
}

.EasyMDEContainer .CodeMirror-scroll {
  @apply !h-full;
}

.EasyMDEContainer .CodeMirror-selectedtext {
  @apply text-background;
}

.EasyMDEContainer .CodeMirror-cursor {
  @apply border-primary;
}

.EasyMDEContainer .md {
  @apply bg-background border-none p-4;
}
</style>
