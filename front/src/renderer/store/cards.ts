import { defineStore } from 'pinia';

export type CardType = 'word' | 'phrase' | 'sentence' | 'grammar' | 'note';

// 词汇条目接口（对应 input-labels.json 中的 entry）
export interface VocabEntry {
  word: string;
  phonetic?: string;
  definition?: string;
  translation?: string;
  pos?: string;
  collins?: number | string;
  oxford?: number | string;
  tag?: string;
  bnc?: number | string;
  frq?: number | string;
  exchange?: string;
  detail?: string;
  audio?: string;
}

// 词汇 JSON 中的单词项
export interface VocabWord {
  original: string;
  entry: VocabEntry;
}

// 词汇 JSON 中的字幕块
export interface VocabBlock {
  index: number;
  start: string;
  end: string;
  text: string;
  words: VocabWord[];
}

// 词汇 JSON 文件格式
export interface VocabJSON {
  source: string;
  path: string;
  blocks: VocabBlock[];
  word_map: Record<string, VocabEntry>;
}

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
  // 扩展字段：词汇详情
  phonetic?: string;
  definition?: string;
  translation?: string;
  pos?: string;
  tag?: string;
  collins?: number | string;
  oxford?: number | string;
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

    // 从词汇 JSON 导入学习卡片
    importFromVocabJSON(vocabData: VocabJSON) {
      const now = new Date().toISOString();
      const sourceTitle = vocabData.source || '导入的词汇';
      const importedCards: CardItem[] = [];

      // 使用 word_map 去重，每个单词只生成一张卡片
      for (const [key, entry] of Object.entries(vocabData.word_map)) {
        // 跳过没有翻译的常见词（如 the, a, is 等）
        if (!entry.translation && !entry.definition) continue;

        const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6) + key.slice(0, 4);

        const card: CardItem = {
          id,
          type: 'word',
          front: entry.word || key,
          back: entry.translation || entry.definition || '',
          videoTitle: sourceTitle,
          ease: 'normal',
          lastReviewedAt: now,
          nextReviewAt: now,
          // 词汇详情
          phonetic: entry.phonetic,
          definition: entry.definition,
          translation: entry.translation,
          pos: entry.pos,
          tag: entry.tag,
          collins: entry.collins,
          oxford: entry.oxford,
        };

        importedCards.push(card);
      }

      // 添加到卡片列表（避免重复）
      const existingFronts = new Set(this.itemsAll.map(c => c.front.toLowerCase()));
      const newCards = importedCards.filter(c => !existingFronts.has(c.front.toLowerCase()));

      this.itemsAll.push(...newCards);
      this.itemsToday.push(...newCards);

      return {
        total: importedCards.length,
        added: newCards.length,
        skipped: importedCards.length - newCards.length,
      };
    },

    // 导出学习卡片为 JSON
    exportToJSON(): string {
      const exportData = {
        exportedAt: new Date().toISOString(),
        version: '1.0',
        totalCards: this.itemsAll.length,
        cards: this.itemsAll.map(card => ({
          id: card.id,
          type: card.type,
          front: card.front,
          back: card.back,
          videoId: card.videoId,
          videoTitle: card.videoTitle,
          videoTime: card.videoTime,
          ease: card.ease,
          lastReviewedAt: card.lastReviewedAt,
          nextReviewAt: card.nextReviewAt,
          phonetic: card.phonetic,
          definition: card.definition,
          translation: card.translation,
          pos: card.pos,
          tag: card.tag,
          collins: card.collins,
          oxford: card.oxford,
        })),
      };
      return JSON.stringify(exportData, null, 2);
    },

    // 从导出的 JSON 导入卡片
    importFromExportedJSON(jsonStr: string) {
      try {
        const data = JSON.parse(jsonStr);
        if (!data.cards || !Array.isArray(data.cards)) {
          throw new Error('无效的卡片 JSON 格式');
        }

        const now = new Date().toISOString();
        const existingIds = new Set(this.itemsAll.map(c => c.id));
        const existingFronts = new Set(this.itemsAll.map(c => c.front.toLowerCase()));

        let added = 0;
        let skipped = 0;

        for (const cardData of data.cards) {
          // 跳过已存在的卡片
          if (existingIds.has(cardData.id) || existingFronts.has(cardData.front?.toLowerCase())) {
            skipped++;
            continue;
          }

          const card: CardItem = {
            id: cardData.id || Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
            type: cardData.type || 'word',
            front: cardData.front || '',
            back: cardData.back || '',
            videoId: cardData.videoId,
            videoTitle: cardData.videoTitle,
            videoTime: cardData.videoTime,
            ease: cardData.ease || 'normal',
            lastReviewedAt: cardData.lastReviewedAt || now,
            nextReviewAt: cardData.nextReviewAt || now,
            phonetic: cardData.phonetic,
            definition: cardData.definition,
            translation: cardData.translation,
            pos: cardData.pos,
            tag: cardData.tag,
            collins: cardData.collins,
            oxford: cardData.oxford,
          };

          this.itemsAll.push(card);
          this.itemsToday.push(card);
          existingIds.add(card.id);
          existingFronts.add(card.front.toLowerCase());
          added++;
        }

        return { total: data.cards.length, added, skipped };
      } catch (e) {
        throw new Error(`导入失败: ${e instanceof Error ? e.message : '未知错误'}`);
      }
    },

    // 清空所有卡片
    clearAll() {
      this.itemsAll = [];
      this.itemsToday = [];
      this.currentIndex = 0;
      this.doneCount = 0;
    },
  },
});