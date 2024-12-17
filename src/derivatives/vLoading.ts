import { Directive, DirectiveBinding, createApp, h } from "vue";
import Loading from "./Loading.vue";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

interface LoadingElement extends HTMLElement {
  _loadingContainer?: any;
}

export const vLoading: Directive = {
  mounted(el: LoadingElement, binding: DirectiveBinding) {
    const fullscreen = !!binding.modifiers.fullscreen;

    const loadingInstance = createApp({
      render() {
        return h(Loading, { fullscreen });
      },
    }).component("fa-icon", FontAwesomeIcon);

    el._loadingContainer = document.createElement("div");
    loadingInstance.mount(el._loadingContainer);

    if (!fullscreen) el.style.position = "relative";

    if (binding.value) {
      el.appendChild(el._loadingContainer);
    }
  },

  updated(el: LoadingElement, binding: DirectiveBinding) {
    if (binding.value !== binding.oldValue && el._loadingContainer) {
      if (binding.value) {
        el.appendChild(el._loadingContainer);
      } else if (el._loadingContainer.parentNode === el) {
        el.removeChild(el._loadingContainer);
      }
    }
  },

  unmounted(el: LoadingElement) {
    if (el._loadingContainer) {
      if (el._loadingContainer.parentNode === el) {
        el.removeChild(el._loadingContainer);
      }
      el._loadingContainer = null;
    }
  },
};
