import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
import "./style.css";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { vLoading } from "./derivatives";

createApp(App)
  .directive("loading", vLoading)
  .component("fa-icon", FontAwesomeIcon)
  .use(createPinia())
  .use(router)
  .mount("#app");
