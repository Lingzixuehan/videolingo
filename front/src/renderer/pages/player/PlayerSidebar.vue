<template>
  <section class="right">
    <header class="right-header">
      <div class="title">{{ title }}</div>
      <div class="right-header-actions">
        <button class="back-btn" @click="$emit('back')">返回视频列表</button>

        <!-- Whisper actions (local service) -->
        <button class="back-btn" @click="$emit('extract')" :disabled="whisperProcessing">提取字幕</button>
        <button class="back-btn" @click="$emit('translate')" :disabled="whisperProcessing">翻译并嵌入</button>
        <button class="back-btn" @click="$emit('analyze')" :disabled="whisperProcessing">分析 / 标注</button>

        <div class="time">
          {{ formatTime(position) }} / {{ formatTime(duration) }}
        </div>
      </div>
    </header>

    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab"
        :class="{ active: activeTab === tab.key }"
        @click="$emit('update:activeTab', tab.key)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <!-- Extraction progress display -->
    <div v-if="whisperProcessing" style="padding:6px 12px;">
      <div>提取中：{{ extractProgress }}%</div>
      <div style="background:#0b1220;height:8px;border-radius:6px;margin-top:6px;overflow:hidden;">
        <div :style="{ width: extractProgress + '%', background: 'linear-gradient(90deg,#38bdf8,#0ea5e9)', height: '100%' }"></div>
      </div>
    </div>

    <div class="tab-content">
      <!-- Tab1：滚动字幕 -->
      <TabSubtitles
        v-if="activeTab === 'subtitles'"
        :subtitles="subtitles"
        :currentSubtitleId="currentSubtitleId"
        @seek="(t) => $emit('seek', t)"
      />

      <!-- Tab2：单词 -->
      <TabWords
        v-else-if="activeTab === 'words'"
        :wordLabels="wordLabels"
        :position="position"
        @addCard="(w, m) => $emit('addCard', w, m)"
      />

      <!-- Tab3：短语 / 俚语 -->
      <div v-else-if="activeTab === 'phrases'" class="tab-panel">
        <p class="placeholder">
          这里将展示短语和俚语列表。后续可按出现频次/时间排序。
        </p>
      </div>

      <!-- Tab4：长难句语法分析 -->
      <div v-else-if="activeTab === 'grammar'" class="tab-panel">
        <p class="placeholder">
          这里将展示当前句子的语法结构分析（主谓宾、从句、时态等）。
        </p>
      </div>

      <!-- Tab5：笔记 / 标注 -->
      <TabNotes
        v-else-if="activeTab === 'notes'"
        :notes="notes"
        :position="position"
        @addNote="(t, time) => $emit('addNote', t, time)"
        @removeNote="(id) => $emit('removeNote', id)"
        @seek="(t) => $emit('seek', t)"
      />

      <!-- Tab6：本视频相关卡片 -->
      <TabCards
        v-else-if="activeTab === 'cards'"
        :videoCards="videoCards"
        @review="$emit('review')"
        @deleteCard="(id) => $emit('deleteCard', id)"
        @seek="(t) => $emit('seek', t)"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import TabSubtitles from './TabSubtitles.vue';
import TabWords from './TabWords.vue';
import TabNotes from './TabNotes.vue';
import TabCards from './TabCards.vue';

defineProps<{
  title: string;
  position: number;
  duration: number;
  whisperProcessing: boolean;
  extractProgress: number;
  activeTab: string;
  subtitles: any[];
  currentSubtitleId: string | number | null;
  wordLabels: any[];
  notes: any[];
  videoCards: any[];
}>();

defineEmits<{
  (e: 'back'): void;
  (e: 'extract'): void;
  (e: 'translate'): void;
  (e: 'analyze'): void;
  (e: 'update:activeTab', tab: string): void;
  (e: 'seek', time: number): void;
  (e: 'addCard', word: string, meaning: string): void;
  (e: 'addNote', text: string, time: number): void;
  (e: 'removeNote', id: string): void;
  (e: 'review'): void;
  (e: 'deleteCard', id: string): void;
}>();

const tabs = [
  { key: 'subtitles', label: '滚动字幕' },
  { key: 'words', label: '单词' },
  { key: 'phrases', label: '短语 / 俚语' },
  { key: 'grammar', label: '长难句语法' },
  { key: 'notes', label: '笔记 / 标注' },
  { key: 'cards', label: '本视频卡片' },
];

function formatTime(sec: number | undefined) {
  if (!sec && sec !== 0) return '--:--';
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const ss = s % 60;
  return `${m.toString().padStart(2, '0')}:${ss.toString().padStart(2, '0')}`;
}
</script>

<style scoped>
.right {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.right-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.right-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  border: 1px solid rgba(148,163,184,.25);
  background: transparent;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
  color: var(--c-text);
}

.back-btn:hover {
  background: rgba(56,189,248,0.06);
}

.right-header .title {
  font-size: 18px;
  font-weight: 700;
  color: var(--c-text);
}

.right-header .time {
  font-size: 13px;
  color: var(--c-text-dim);
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.tab {
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 999px;
  border: none;
  background: rgba(255,255,255,0.03);
  color: var(--c-text-dim);
  cursor: pointer;
}

.tab.active {
  background: linear-gradient(135deg, rgba(56,189,248,0.18), rgba(14,165,233,0.18));
  color: var(--c-text);
  box-shadow: 0 6px 20px rgba(2,6,23,0.45);
}

.tab-content {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  background: rgba(10,16,28,0.96);
  border: 1px solid rgba(148,163,184,0.08);
  color: var(--c-text);
  overflow: auto;
}

.placeholder {
  font-size: 14px;
  color: var(--c-text-dim);
}
</style>
