import { defineStore } from 'pinia';

export interface SubtitleLine {
  id: number;
  videoId: string;
  start: number; // 开始时间，秒
  end: number; // 结束时间，秒
  text: string; // 英文原文
  textCn?: string; // 可选：中文翻译
}

interface SubtitlesState {
  // 按视频 id 存字幕列表
  byVideoId: Record<string, SubtitleLine[]>;
}

export const useSubtitlesStore = defineStore('subtitles', {
  state: (): SubtitlesState => ({
    byVideoId: {},
  }),

  getters: {
    /**
     * 获取某个视频的字幕列表
     */
    subtitlesForVideo: (state) => {
      return (videoId: string): SubtitleLine[] => state.byVideoId[videoId] || [];
    },
  },

  actions: {
    /**
     * 设置某个视频的完整字幕列表
     */
    setSubtitles(videoId: string, lines: SubtitleLine[]) {
      this.byVideoId[videoId] = lines;
    },

    /**
     * 仅用于前端开发：为指定视频填充假字幕
     */
    seedMockForVideo(videoId: string) {
      if (this.byVideoId[videoId]?.length) return;
      this.byVideoId[videoId] = [
        {
          id: 1,
          videoId,
          start: 0,
          end: 5,
          text: 'This is the first example sentence.',
          textCn: '这是第一句示例字幕。',
        },
        {
          id: 2,
          videoId,
          start: 5,
          end: 10,
          text: 'Here comes the second subtitle line.',
          textCn: '第二句字幕来了。',
        },
        {
          id: 3,
          videoId,
          start: 10,
          end: 16,
          text: 'Learning English with videos can be fun and effective.',
          textCn: '通过视频学习英语既有趣又高效。',
        },
      ];
    },
  },
});