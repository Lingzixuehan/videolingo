import { defineStore } from 'pinia';
import { isAllowedSize, isAllowedDuration } from '../utils/validators';

export interface VideoItem {
  id: string;
  name: string;
  size: number;        // bytes
  duration: number;    // seconds
  createdAt: string;   // ISO
}

const STORAGE_KEY = 'videos_v1';

function uuid(): string {
  // 优先使用浏览器 crypto
  // @ts-ignore
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
  return 'v_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

export const useVideosStore = defineStore('videos', {
  state: () => ({
    items: [] as VideoItem[],
    error: '' as string
  }),
  getters: {
    count: (s) => s.items.length
  },
  actions: {
    load() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        this.items = raw ? JSON.parse(raw) : [];
      } catch {
        this.items = [];
      }
    },
    save() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.items));
    },
    clearError() {
      this.error = '';
    },
    addFromFile(file: File, durationSec: number) {
      this.clearError();
      if (!isAllowedSize(file.size)) {
        this.error = '文件过大，最大支持 500MB';
        return;
      }
      if (!isAllowedDuration(durationSec)) {
        this.error = '视频过长，最大支持 20 分钟';
        return;
      }
      const item: VideoItem = {
        id: uuid(),
        name: file.name,
        size: file.size,
        duration: durationSec,
        createdAt: new Date().toISOString()
      };
      this.items.unshift(item);
      this.save();
    },
    remove(id: string) {
      this.items = this.items.filter(v => v.id !== id);
      this.save();
    },
    clear() {
      this.items = [];
      this.save();
    }
  }
});