<script setup lang="ts">
import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { wDialog } from ".";
import Modal from "./Modal.vue";
import Layout from "@/components/Layout.vue";
import IconButton from "@/components/IconButton.vue";
import NamedTransition from "@/components/NamedTransition.vue";
</script>

<template>
  <Modal class="flex items-center justify-center p-2" :show="wDialog.show">
    <NamedTransition name="bounce">
      <Layout
        class="w-full md:w-fit md:max-w-full max-h-full overflow-x-hidden overflow-y-auto widget rounded border-t border-t-dim"
        data-float="true"
        v-if="wDialog.data"
        v-show="wDialog.show"
      >
        <template #header="{ float }">
          <div
            class="flex items-center p-2"
            :class="{
              'bg-background shadow shadow-black': float,
            }"
          >
            <span
              class="flex-1 text-ellipsis font-bold"
              v-text="wDialog.data.title"
            />
            <IconButton :icon="faXmark" @click="wDialog.reject('cancel')" />
          </div>
        </template>

        <div class="p-2">
          <component
            :is="wDialog.data.content"
            v-bind="wDialog.data.props || {}"
            v-on="wDialog.data.events || {}"
          />
        </div>
      </Layout>
    </NamedTransition>
  </Modal>
</template>
