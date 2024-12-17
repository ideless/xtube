<script setup lang="ts">
import { wConfirm } from ".";
import Modal from "./Modal.vue";
</script>

<template>
  <Modal class="flex items-end justify-center p-2" :show="wConfirm.show" block>
    <div
      class="shadow-md shadow-black bg-gray-800 border-t border-gray-600 py-2 px-4 rounded space-x-4 transition-transform max-w-full text-wrap break-words"
      :class="{
        'scale-0': !wConfirm.show,
      }"
    >
      <span>{{ wConfirm.data }}</span>
      <button
        class="text-sky-300 hover:underline"
        @click="wConfirm.resolve('ok')"
        v-text="'OK'"
      />
      <button
        class="text-gray-400 hover:underline"
        @click="wConfirm.reject('cancel')"
        v-text="'NO'"
      />
    </div>
  </Modal>
</template>
