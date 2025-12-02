<template>
  <div class="tab-panel">
    <div v-if="videoCards.length === 0" class="placeholder">
      还没有从本视频生成任何卡片。你可以点击下方字幕中的单词，收藏为卡片。
    </div>
    <ul v-else class="video-cards-list">
      <li v-for="c in videoCards" :key="c.id" class="video-card-item">
        <div class="video-card-main">
          <div class="video-card-front">{{ c.front }}</div>
          <div v-if="c.back" class="video-card-back">{{ c.back }}</div>
          <div class="video-card-meta">
            <button
              v-if="typeof c.videoTime === 'number'"
              class="video-card-time"
              @click="$emit('seek', c.videoTime!)"
            >
              跳到 {{ formatTimeShort(c.videoTime!) }}
            </button>
            <span v-if="c.videoTitle" class="video-card-title">{{ c.videoTitle }}</span>
          </div>
        </div>
        <div class="video-card-actions">
          <button class="video-card-btn" @click="$emit('review')">去复习</button>
          <button class="video-card-btn delete" @click="$emit('deleteCard', c.id)">删除</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  videoCards: any[];
}>();

defineEmits<{
  (e: 'review'): void;
  (e: 'deleteCard', id: string): void;
  (e: 'seek', time: number): void;
}>();

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

.placeholder {
  font-size: 14px;
  color: var(--c-text-dim);
}

.video-cards-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.video-card-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #f9fafb;
  color: #111827;
}

.video-card-front {
  font-weight: 500;
  margin-bottom: 2px;
}

.video-card-back {
  font-size: 13px;
  color: #4b5563;
  margin-bottom: 4px;
}

.video-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
}

.video-card-time {
  border-radius: 999px;
  border: none;
  padding: 2px 8px;
  background: #e5e7eb;
  cursor: pointer;
  font-size: 12px;
}

.video-card-title {
  font-size: 12px;
}

.video-card-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
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

.video-card-btn.delete {
  background: #ef4444;
}
</style>
