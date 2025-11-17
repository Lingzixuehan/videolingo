import { defineStore } from 'pinia';

export type VideoStatus = 'idle' | 'processing' | 'ready';

export interface VideoItem {
  id: string;
  title: string;
  filePath?: string;
  duration?: number; // 秒
  size?: number;     // 字节
  createdAt?: string;
  status?: VideoStatus;
  notesCount?: number;
}

interface VideosState {
  items: VideoItem[];
  currentVideoId: string | null;
}

export const useVideosStore = defineStore('videos', {
  state: (): VideosState => ({
    items: [],
    currentVideoId: null,
  }),

  getters: {
    currentVideo(state): VideoItem | null {
      if (!state.currentVideoId) return null;
      return state.items.find(v => v.id === state.currentVideoId) ?? null;
    },
  },

  actions: {
    // /**
    //  * 仅用于前端开发阶段填充假数据，方便页面调试
    //  */
    // seedMockData() {
    //   if (this.items.length > 0) return;
    //   const now = new Date();
    //   this.items = [
    //     {
    //       id: '1',
    //       title: '示例视频一：Learning English with Movies',
    //       duration: 600,
    //       size: 50 * 1024 * 1024,
    //       createdAt: now.toISOString(),
    //       status: 'ready',
    //       notesCount: 3,
    //     },
    //     {
    //       id: '2',
    //       title: '示例视频二：TED Talk Sample',
    //       duration: 1200,
    //       size: 120 * 1024 * 1024,
    //       createdAt: now.toISOString(),
    //       status: 'processing',
    //       notesCount: 0,
    //     },
    //     {
    //       id: '3',
    //       title: '示例视频三：Everyday English Conversations',
    //       duration: 900,
    //       size: 80 * 1024 * 1024,
    //       createdAt: now.toISOString(),
    //       status: 'idle',
    //       notesCount: 1,
    //     },
    //   ];
    // },

    /**
     * 设置当前选中的视频
     */
    setCurrentVideo(id: string | null) {
      this.currentVideoId = id;
    },

    /**
     * 添加一个视频（后续可以从 Electron 文件选择结果构建 VideoItem）
     */
    addVideo(payload: Omit<VideoItem, 'id' | 'createdAt' | 'status' | 'notesCount'>) {
      const id = Date.now().toString() + Math.random().toString(36).slice(2, 6);
      const createdAt = new Date().toISOString();
      this.items.push({
        id,
        createdAt,
        status: 'idle',
        notesCount: 0,
        ...payload,
      });
      return id;
    },

    /**
     * 从文件路径数组批量添加视频（标题来自文件名）
     */
    addVideosFromPaths(fileInfos: { path: string; size?: number; duration?: number }[]) {
      for (const info of fileInfos) {
        const title = this.extractTitleFromPath(info.path);
        this.addVideo({
          title,
          filePath: info.path,
          size: info.size,
          duration: info.duration,
        });
      }
    },

    /**
     * 更新视频（例如状态从 processing -> ready）
     */
    updateVideo(id: string, patch: Partial<VideoItem>) {
      const idx = this.items.findIndex(v => v.id === id);
      if (idx === -1) return;
      this.items[idx] = { ...this.items[idx], ...patch };
    },

    /**
     * 删除视频（以及相关本地数据的清理后续可以一起做）
     */
    removeVideo(id: string) {
      this.items = this.items.filter((v) => v.id !== id);
      if (this.currentVideoId === id) {
        this.currentVideoId = null;
      }
    },

    /**
     * 从路径中取出文件名作为标题
     */
    extractTitleFromPath(path: string): string {
      const parts = path.split(/[\\/]/);
      const file = parts[parts.length - 1] || '';
      return file.replace(/\.[^.]+$/, '');
    },


    ensureBuiltinSample() {
      if (this.items.length > 0) return;

      this.addVideo({
        title: '示例视频 test',
        filePath: '/videos/test.mp4',   // 静态资源路径
        duration: undefined,           // 可以先空着
        size: undefined,
      });
    },
  },
});