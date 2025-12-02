<template>
  <div class="tab-panel">
    <div class="notes-input">
      <textarea
        v-model="newNoteText"
        class="notes-textarea"
        rows="3"
        placeholder="在当前时间记一条笔记，例如听不懂的句子、自己想到的问题……"
      ></textarea>
      <button class="notes-add-btn" @click="onAddNote" :disabled="!newNoteText.trim()">
        在 {{ formatTimeShort(position) }} 处添加笔记
      </button>
    </div>

    <div class="notes-list-wrap">
      <div v-if="notes.length === 0" class="notes-empty">
        还没有笔记。播放到有疑问的地方时，在上方输入框写下你的想法，然后点击「添加笔记」。
      </div>
      <ul v-else class="notes-list">
        <li v-for="n in notes" :key="n.id" class="note-item">
          <button class="note-time" @click="$emit('seek', n.time)">
            {{ formatTimeShort(n.time) }}
          </button>
          <div class="note-text">
            {{ n.text }}
          </div>
          <button class="note-delete" @click="$emit('removeNote', n.id)">删除</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  notes: any[];
  position: number;
}>();

const emit = defineEmits<{
  (e: 'addNote', text: string, time: number): void;
  (e: 'removeNote', id: string): void;
  (e: 'seek', time: number): void;
}>();

const newNoteText = ref('');

function onAddNote() {
  const text = newNoteText.value.trim();
  if (!text) return;
  emit('addNote', text, props.position);
  newNoteText.value = '';
}

function formatTimeShort(sec: number) {
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const ss = s % 60;
  return `${m.toString().padStart(2, '0')}:${ss.toString().padStart(2, '0')}`;
}
</script>

<style scoped>
.tab-panel {
  height: 100%;
  overflow-y: auto;
}

.notes-input {
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.notes-textarea {
  width: 100%;
  resize: vertical;
  min-height: 60px;
  padding: 6px 8px;
  font-size: 13px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: rgba(255,255,255,0.9);
  color: #111827;
}

.notes-add-btn {
  align-self: flex-end;
  border-radius: 999px;
  border: none;
  padding: 4px 10px;
  font-size: 12px;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
}

.notes-add-btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.notes-list-wrap {
  margin-top: 4px;
}

.notes-empty {
  font-size: 13px;
  color: var(--c-text-dim);
}

.notes-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.note-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 8px;
  align-items: flex-start;
  padding: 6px 8px;
  border-radius: 6px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(148,163,184,0.1);
}

.note-time {
  border-radius: 999px;
  border: none;
  background: rgba(255,255,255,0.1);
  color: var(--c-text);
  padding: 2px 8px;
  font-size: 12px;
  cursor: pointer;
  font-variant-numeric: tabular-nums;
}

.note-text {
  font-size: 13px;
  color: var(--c-text);
}

.note-delete {
  border: none;
  background: transparent;
  color: #ef4444;
  font-size: 12px;
  cursor: pointer;
}
</style>
