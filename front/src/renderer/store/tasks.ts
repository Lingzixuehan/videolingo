import { defineStore } from 'pinia';

export type TaskStatus = 'pending' | 'processing' | 'done' | 'error' | 'canceled';

export interface TaskItem {
  id: string;
  videoId: string;
  type: 'transcribe';
  status: TaskStatus;
  progress: number; // 0-100
  error?: string;
  createdAt: string;
  updatedAt: string;
}

const STORAGE_KEY = 'tasks_v1';

function uuid() {
  // @ts-ignore
  return (crypto?.randomUUID?.() || 't_' + Date.now().toString(36) + Math.random().toString(36).slice(2,8));
}

function loadAll(): TaskItem[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function persist(list: TaskItem[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

export const useTasksStore = defineStore('tasks', {
  state: () => ({
    items: loadAll() as TaskItem[]
  }),
  getters: {
    active: s => s.items.filter(i => i.status === 'pending' || i.status === 'processing'),
    byVideo: s => (vid: string) => s.items.filter(i => i.videoId === vid)
  },
  actions: {
    create(videoId: string) {
      const item: TaskItem = {
        id: uuid(),
        videoId,
        type: 'transcribe',
        status: 'pending',
        progress: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      this.items.unshift(item);
      persist(this.items);
      return item.id;
    },
    start(id: string) {
      const t = this.items.find(i => i.id === id);
      if (!t || t.status !== 'pending') return;
      t.status = 'processing';
      t.updatedAt = new Date().toISOString();
      persist(this.items);
    },
    updateProgress(id: string, p: number) {
      const t = this.items.find(i => i.id === id);
      if (!t || t.status !== 'processing') return;
      t.progress = p;
      t.updatedAt = new Date().toISOString();
      persist(this.items);
    },
    finish(id: string) {
      const t = this.items.find(i => i.id === id);
      if (!t) return;
      t.status = 'done';
      t.progress = 100;
      t.updatedAt = new Date().toISOString();
      persist(this.items);
    },
    fail(id: string, msg: string) {
      const t = this.items.find(i => i.id === id);
      if (!t) return;
      t.status = 'error';
      t.error = msg;
      t.updatedAt = new Date().toISOString();
      persist(this.items);
    },
    cancel(id: string) {
      const t = this.items.find(i => i.id === id);
      if (!t) return;
      t.status = 'canceled';
      t.updatedAt = new Date().toISOString();
      persist(this.items);
    }
  }
});