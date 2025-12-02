<template>
  <div class="tab-panel">
    <ul class="subtitle-list">
      <li
        v-for="s in subtitles"
        :key="s.id"
        :class="['subtitle-item', { active: s.id === currentSubtitleId }]"
        @click="$emit('seek', s.start)"
        :ref="el => setSubtitleItemRef(el as HTMLLIElement | null, s.id)"
      >
        <div class="time">{{ formatTime(s.start) }}</div>
        <div class="text">
          <div>{{ s.text }}</div>
          <div v-if="s.textCn" class="text-cn">{{ s.textCn }}</div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  subtitles: any[];
  currentSubtitleId: string | number | null;
}>();

defineEmits<{
  (e: 'seek', time: number): void;
}>();

const subtitleItemRefs = ref<Record<string, HTMLLIElement | null>>({});

function setSubtitleItemRef(el: HTMLLIElement | null, id: string | number) {
  if (!el) return;
  subtitleItemRefs.value[String(id)] = el;
}

function formatTime(sec: number | undefined) {
  if (!sec && sec !== 0) return '--:--';
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const ss = s % 60;
  return `${m.toString().padStart(2, '0')}:${ss.toString().padStart(2, '0')}`;
}

watch(() => props.currentSubtitleId, (id) => {
  if (!id) return;
  const el = subtitleItemRefs.value[String(id)];
  if (!el) return;
  const container = el.closest('.tab-panel'); // Changed from .subtitle-list to .tab-panel for scrolling
  if (!container) return;

  const rect = el.getBoundingClientRect();
  const crect = (container as HTMLElement).getBoundingClientRect();
  const offset = rect.top - crect.top - crect.height / 3;
  (container as HTMLElement).scrollBy({ top: offset, behavior: 'smooth' });
});
</script>

<style scoped>
.tab-panel {
  height: 100%;
  overflow-y: auto;
}

.subtitle-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.subtitle-item {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 12px;
  padding: 10px 8px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--c-text);
}

.subtitle-item:hover {
  background: rgba(56,189,248,0.04);
}

.subtitle-item.active {
  background: rgba(56,189,248,0.12);
  box-shadow: 0 8px 20px rgba(2,6,23,0.45);
}

.subtitle-item .time {
  color: var(--c-text-dim);
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}

.subtitle-item .text-cn {
  font-size: 12px;
  color: #6b7280;
}
</style>
