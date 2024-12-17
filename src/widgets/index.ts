import { reactive } from "vue";
import type { Component, Ref } from "vue";

class Widget<D, V, E> {
  data: D;
  show: boolean = false;
  private resolve_func: ((value: V) => void) | null = null;
  private reject_func: ((reason: E) => void) | null = null;

  constructor(data: D) {
    this.data = data;
    this.show = false;
    this.resolve_func = null;
    this.reject_func = null;
  }

  install() {
    document.body.appendChild(document.createElement("div"));
  }

  open(newData: D): Promise<V> {
    this.data = newData;
    this.show = true;

    return new Promise((resolve, reject) => {
      this.resolve_func = resolve;
      this.reject_func = reject;
    });
  }

  resolve(value: V) {
    this.show = false;
    this.resolve_func?.(value);
  }

  reject(error: E) {
    this.show = false;
    this.reject_func?.(error);
  }
}

export const wConfirm = reactive(new Widget<string, "ok", "cancel">(""));

export const wAlert = reactive(
  new Widget<
    { kind: "info" | "success" | "error"; message: string },
    "closed",
    undefined
  >({ kind: "info", message: "" }),
);

export const wDialog = reactive(
  new Widget<
    {
      title: string;
      content: Component;
      props?: Record<string, any>;
      events?: Record<string, any>;
    },
    any,
    "cancel"
  >({ title: "", content: () => null }),
);

export const wLoading = reactive(
  new Widget<string | Ref<string>, "ok", "cancel">(""),
);
