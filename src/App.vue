<script setup lang="ts">
import Confirm from "@/widgets/Confirm.vue";
import Alert from "@/widgets/Alert.vue";
import Dialog from "@/widgets/Dialog.vue";
import Loading from "@/widgets/Loading.vue";
import { wLoading, wAlert } from "./widgets";
import { useRouter } from "vue-router";
import { useApiStore } from "./store";

const apiStore = useApiStore();
const router = useRouter();

router.beforeEach((to) => {
  if (to.name !== "login" && !apiStore.loggedIn) {
    return { name: "login" };
  } else {
    wLoading.open("");
  }
});

router.afterEach(async (to) => {
  if (to.name === "home") {
    try {
      await apiStore.fetchRecords();
    } catch (e) {
      wAlert.open({ kind: "error", message: String(e) });
      router.replace({ name: "login" });
    }
  }

  wLoading.resolve("ok");
});
</script>

<template>
  <div class="fixed inset-0 bg-background -z-50" />
  <RouterView v-slot="{ Component }">
    <KeepAlive include="Home">
      <Component :is="Component" :key="$route.name" />
    </KeepAlive>
  </RouterView>
  <!-- widgets -->
  <Confirm />
  <Alert />
  <Dialog />
  <Loading />
</template>
