/// <reference types="vite/client" />

declare const __BUILD_TIME__: string;

interface ImportMetaEnv {
  readonly VITE_LOGIN_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
