import { defineStore } from 'pinia';

export type CardType = 'word' | 'phrase' | 'sentence' | 'grammar' | 'note';

export interface CardItem {
  id: string;
  type: CardType;
  front: string;
  back: string;
  videoId?: string;
  videoTitle?: string;
  videoTime?: number;
  ease?: 'hard' | 'normal' | 'easy';
  lastReviewedAt?: string;
  nextReviewAt?: string;
}

interface CardsState {
  todayTarget: number;
  itemsAll: CardItem[];   
  itemsToday: CardItem[];
  currentIndex: number;
  doneCount: number;
}

export const useCardsStore = defineStore('cards', {
  state: (): CardsState => ({
    todayTarget: 20,
    itemsAll: [],       
    itemsToday: [],
    currentIndex: 0,
    doneCount: 0,
  }),

  getters: {
    currentToday(state): CardItem | null {
      if (!state.itemsToday.length) return null;
      return state.itemsToday[state.currentIndex] ?? null;
    },
    remainingCount(state): number {
      return Math.max(state.itemsToday.length - state.doneCount, 0);
    },
  },

  actions: {
    // 用于测试或重置
    seedMockToday() {
      const now = new Date().toISOString();
      this.itemsAll = [
        {
          id: 'demo-1',
          type: 'word',
          front: 'example',
          back: '示例；例子',
          ease: 'normal',
          lastReviewedAt: now,
          nextReviewAt: now,
        },
        {
          id: 'demo-2',
          type: 'sentence',
          front: 'This is a sample sentence for review.',
          back: '这是一句用于复习的示例句子。',
          ease: 'normal',
          lastReviewedAt: now,
          nextReviewAt: now,
        },
      ];
      this.itemsToday = [...this.itemsAll];
      this.currentIndex = 0;
      this.doneCount = 0;
    },

    answerCurrent(ease: 'hard' | 'normal' | 'easy') {
      const card = this.currentToday;
      if (!card) return;

      const idx = this.itemsToday.findIndex((c) => c.id === card.id);
      if (idx === -1) return;

      const now = new Date();
      const base = now.getTime();
      let nextMs = base + 24 * 60 * 60 * 1000; // 默认 1 天
      if (ease === 'hard') {
        nextMs = base + 12 * 60 * 60 * 1000;
      } else if (ease === 'easy') {
        nextMs = base + 2 * 24 * 60 * 60 * 1000;
      }

      const updated: CardItem = {
        ...card,
        ease,
        lastReviewedAt: now.toISOString(),
        nextReviewAt: new Date(nextMs).toISOString(),
      };

      this.itemsToday.splice(idx, 1, updated);

      const allIdx = this.itemsAll.findIndex((c) => c.id === card.id);
      if (allIdx !== -1) {
        this.itemsAll.splice(allIdx, 1, updated);
      }

      this.doneCount += 1;
      if (this.currentIndex < this.itemsToday.length - 1) {
        this.currentIndex += 1;
      }
    },

    restartToday() {
      this.currentIndex = 0;
      this.doneCount = 0;
    },

    addFromVideo(payload: {
      wordOrSentence: string;
      meaning?: string;
      type?: CardType;
      videoId?: string;
      videoTitle?: string;
      videoTime?: number;
    }) {
      const id =
        Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      const now = new Date().toISOString();
      const card: CardItem = {
        id,
        type: payload.type ?? 'word',
        front: payload.wordOrSentence,
        back: payload.meaning ?? '',
        videoId: payload.videoId,
        videoTitle: payload.videoTitle,
        videoTime: payload.videoTime,
        ease: 'normal',
        lastReviewedAt: now,
        nextReviewAt: now,
      };

      this.itemsAll.push(card);
      this.itemsToday.push(card);
    },

    removeById(id: string) {
      this.itemsAll = this.itemsAll.filter((c) => c.id !== id);
      this.itemsToday = this.itemsToday.filter((c) => c.id !== id);
      if (this.currentIndex >= this.itemsToday.length) {
        this.currentIndex = Math.max(this.itemsToday.length - 1, 0);
      }
    },
  },
});