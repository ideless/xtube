import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

// https://www.flypenguin.de/2021/08/18/javascript-iso-date-with-local-timezone/
function getISOLocalString() {
  let date = new Date();
  let tzo = -date.getTimezoneOffset();

  if (tzo === 0) {
    return date.toISOString();
  } else {
    let dif = tzo >= 0 ? "+" : "-";
    let pad = function (num: number, digits = 2) {
      return String(num).padStart(digits, "0");
    };

    return (
      date.getFullYear() +
      "-" +
      pad(date.getMonth() + 1) +
      "-" +
      pad(date.getDate()) +
      "T" +
      pad(date.getHours()) +
      ":" +
      pad(date.getMinutes()) +
      ":" +
      pad(date.getSeconds()) +
      "." +
      pad(date.getMilliseconds(), 3) +
      dif +
      pad(tzo / 60) +
      ":" +
      pad(tzo % 60)
    );
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
      vue: "vue/dist/vue.esm-bundler",
    },
  },
  server: {
    proxy: {
      "/api/": {
        target: "http://localhost:8000/api",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      "/data/": {
        target: "http://localhost:8000/data",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/data/, ""),
      },
    },
  },
  define: {
    __BUILD_TIME__: JSON.stringify(getISOLocalString()),
  },
});
