import { createRouter, createWebHashHistory } from "vue-router";

import Login from "@/views/Login.vue";
import Home from "@/views/Home.vue";

const routes = [
  {
    path: "/login",
    name: "login",
    component: Login,
  },
  {
    path: "/",
    name: "home",
    component: Home,
  },
  {
    path: "/note/:uid",
    name: "note",
    component: () => import("@/views/Note.vue"),
  },
  {
    path: "/video/:uid",
    name: "video",
    component: () => import("@/views/Video.vue"),
  },
  {
    path: "/image/:uid",
    name: "image",
    component: () => import("@/views/Image.vue"),
  },
  {
    path: "/book/:uid",
    name: "book",
    component: () => import("@/views/Book.vue"),
  },
  {
    path: "/file/:uid",
    name: "file",
    component: () => import("@/views/File.vue"),
  },
  {
    path: "/edit/:uid?",
    name: "edit",
    component: () => import("@/views/Edit.vue"),
  },
  {
    path: "/upload",
    name: "upload",
    component: () => import("@/views/Upload.vue"),
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

export default router;
