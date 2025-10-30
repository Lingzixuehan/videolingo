import { defineStore } from 'pinia';

export type DlItem = { id: string; name: string; status: 'queued'|'downloading'|'done'|'error'; progress: number };

export const useDownloadsStore = defineStore('downloads', {
  state: () => ({ list: [] as DlItem[] }),
  actions: {
    enqueue(item: { id: string; name: string }) {
      this.list.push({ ...item, status: 'queued', progress: 0 });
    }
  }
});