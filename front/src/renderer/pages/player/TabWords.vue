<template>
  <div class="tab-panel">
    <div v-if="wordLabels.length === 0" class="placeholder">尚未生成词汇标注。点击右上角的「分析 / 标注」开始。</div>
    <ul v-else class="word-labels-list">
      <li v-for="(w, idx) in wordLabels" :key="idx" class="word-label-item">
        <div class="word-main">{{ w.entry?.word || w.word || w.original || w }}</div>
        <div class="word-meta">{{ w.entry?.translation || w.entry?.definition || '' }}</div>
        <button class="video-card-btn" @click="onAddCard(w)">收藏</button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  wordLabels: any[];
  position: number;
}>();

const emit = defineEmits<{
  (e: 'addCard', word: string, meaning: string): void;
}>();

function onAddCard(w: any) {
  const word = w.entry?.word || w.word || w.original || w;
  const meaning = w.entry?.translation || w.entry?.definition || '';
  emit('addCard', word, meaning);
}
</script>

<style scoped>
.tab-panel {
  height: 100%;
  overflow-y: auto;
}

.placeholder {
  font-size: 14px;
  color: var(--c-text-dim);
}

.word-labels-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.word-label-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr) auto;
  gap: 10px;
  align-items: center;
  padding: 8px 10px;
  border-radius: 8px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(148,163,184,0.1);
}

.word-main {
  font-weight: 600;
  color: var(--c-text);
}

.word-meta {
  font-size: 13px;
  color: var(--c-text-dim);
}

.video-card-btn {
  border-radius: 999px;
  border: none;
  padding: 3px 10px;
  font-size: 12px;
  cursor: pointer;
  background: #2563eb;
  color: #ffffff;
}
</style>
