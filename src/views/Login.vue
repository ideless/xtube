<script lang="ts" setup>
import { ref } from "vue";
import { useApiStore } from "@/store";
import { useRouter } from "vue-router";
import { wAlert } from "@/widgets";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";

const apiStore = useApiStore();
const router = useRouter();
const key = ref(import.meta.env.VITE_LOGIN_KEY);
const loading = ref(false);
const buildTime = __BUILD_TIME__;

async function handleLogin() {
  try {
    loading.value = true;

    const verified = await apiStore.verifyKey(key.value);

    if (!verified) {
      throw new Error("Invalid key");
    }

    apiStore.loggedIn = true;

    router.push({ name: "home" });
  } catch (error) {
    wAlert.open({ kind: "error", message: String(error) });
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div
    class="flex flex-col items-center justify-center min-h-screen bg-gray-100 relative"
  >
    <form @submit.prevent="handleLogin" class="w-80">
      <input
        type="password"
        v-model="key"
        placeholder="Enter your 128 bit hex key"
        class="border border-gray-300 p-2 rounded mb-4 w-full text-dim"
        required
        pattern="^[0-9a-zA-Z]{32}$"
      />

      <button
        type="submit"
        class="bg-blue-500 text-white p-2 rounded w-full hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-blue-500"
        :disabled="loading"
      >
        <fa-icon :icon="faSpinner" class="animate-spin mr-2" v-show="loading" />
        <span>Login</span>
      </button>
    </form>

    <div
      class="absolute text-gray-400 text-xs bottom-4 left-1/2 -translate-x-1/2"
      v-text="`Build: ${buildTime}`"
    />
  </div>
</template>
