import { defineStore } from 'pinia';

export type CardType = 'word' | 'phrase' | 'sentence' | 'grammar' | 'note';

export interface CardItem {
  id: string;
  type: CardType;
  front: string; // 正面：题干，例如英文单词/句子
  back: string; // 反面：释义/答案
  videoId?: string;
  videoTitle?: string;
  videoTime?: number; // 来源视频时间（秒）
  ease?: 'hard' | 'normal' | 'easy';
  lastReviewedAt?: string;
  nextReviewAt?: string;
}

interface CardsState {
  todayTarget: number;
  itemsToday: CardItem[];
  currentIndex: number;
  doneCount: number;
}

export const useCardsStore = defineStore('cards', {
  state: (): CardsState => ({
    todayTarget: 20,
    itemsToday: [],
    currentIndex: 0,
    doneCount: 0,
  }),

  getters: {
    currentCard(state): CardItem | null {
      if (!state.itemsToday.length) return null;
      return state.itemsToday[state.currentIndex] ?? null;
    },
    remainingCount(state): number {
      return Math.max(state.todayTarget - state.doneCount, 0);
    },
  },

  actions: {
    seedMockToday() {
      if (this.itemsToday.length) return;
      const now = new Date().toISOString();
      this.itemsToday = [
        {
          id: 'c1',
          type: 'word',
          front: 'notorious',
          back: '臭名昭著的；声名狼藉的',
          videoId: '1',
          videoTitle: '示例视频一：Learning English with Movies',
          videoTime: 120,
          ease: 'normal',
          lastReviewedAt: now,
        },
        {
          id: 'c2',
          type: 'sentence',
          front: 'Learning English with videos can be fun and effective.',
          back: '通过视频学习英语既有趣又高效。',
          videoId: '1',
          videoTitle: '示例视频一：Learning English with Movies',
          videoTime: 600,
          ease: 'hard',
        },
        {
          id: 'c3',
          type: 'grammar',
          front: 'Find the subject and the main verb in this sentence: "Here comes the second subtitle line."',
          back: '主语是 "the second subtitle line"，谓语是 "comes"。',
          videoId: '1',
          videoTitle: '示例视频一：Learning English with Movies',
          videoTime: 300,
          ease: 'easy',
        },
      ];
      this.todayTarget = 20;
      this.currentIndex = 0;
      this.doneCount = 0;
    },

    answerCurrent(ease: 'hard' | 'normal' | 'easy') {
      const card = this.currentCard;
      if (!card) return;
      const now = new Date().toISOString();
      card.ease = ease;
      card.lastReviewedAt = now;
      // TODO: 这里以后接真正的 SRS 算法，计算 nextReviewAt
      card.nextReviewAt = now;

      this.doneCount += 1;

      if (this.currentIndex < this.itemsToday.length - 1) {
        this.currentIndex += 1;
      } else {
        // 已到最后一张，保持在最后
        this.currentIndex = this.itemsToday.length - 1;
      }
    },

    restartToday() {
      this.currentIndex = 0;
      this.doneCount = 0;
    },
  },
});