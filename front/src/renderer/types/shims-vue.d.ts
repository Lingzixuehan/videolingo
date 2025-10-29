declare module '*.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

declare global {
  interface Window {
    api?: { ping: () => Promise<string> };
    versions?: { electron: string; chrome: string; node: string };
  }
}
export {};