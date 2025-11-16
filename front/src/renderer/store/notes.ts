import { defineStore } from 'pinia';

export interface NoteItem {
  id: string;
  videoId: string;
  time: number; // 秒
  text: string;
  createdAt: string;
}

interface NotesState {
  byVideoId: Record<string, NoteItem[]>;
}

export const useNotesStore = defineStore('notes', {
  state: (): NotesState => ({
    byVideoId: {},
  }),

  getters: {
    notesForVideo: (state) => {
      return (videoId: string): NoteItem[] =>
        (state.byVideoId[videoId] || []).slice().sort((a, b) => a.time - b.time);
    },
  },

  actions: {
    addNote(payload: { videoId: string; time: number; text: string }) {
      const { videoId, time, text } = payload;
      const list = this.byVideoId[videoId] || [];
      const now = new Date().toISOString();
      const note: NoteItem = {
        id: `${videoId}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        videoId,
        time,
        text,
        createdAt: now,
      };
      this.byVideoId[videoId] = [...list, note];
    },

    removeNote(videoId: string, noteId: string) {
      const list = this.byVideoId[videoId];
      if (!list) return;
      this.byVideoId[videoId] = list.filter((n) => n.id !== noteId);
    },
  },
});