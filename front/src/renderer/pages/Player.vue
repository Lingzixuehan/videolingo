<template>
  <div class="player-page">
    <!-- 左侧：视频 + 底部字幕 -->
    <section class="left">
      <div class="video-wrapper">
        <video
          ref="videoRef"
          class="video"
          controls
          :src="videoSrc"
        >
          您的系统暂不支持 video 标签。
        </video>
      </div>

      <!-- 底部当前句字幕条 -->
      <div v-if="currentSubtitle" class="subtitle-bar">
        <span
          v-for="(word, idx) in currentSubtitleWords"
          :key="idx"
          class="subtitle-word"
          @click="onWordClick(word, $event)"
        >
          {{ word }}
        </span>
      </div>
    </section>

    <!-- 右侧：Tab 区域 -->
    <section class="right">
      <header class="right-header">
        <div class="title">{{ currentVideo?.title || '未选择视频' }}</div>
        <div class="right-header-actions">
          <button class="back-btn" @click="goBackToVideos">返回视频列表</button>
          <div class="time">
            {{ positionDisplay }} / {{ durationDisplay }}
          </div>
        </div>
      </header>

      <nav class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </nav>

      <div class="tab-content">
        <!-- Tab1：滚动字幕 -->
        <div v-if="activeTab === 'subtitles'" class="tab-panel">
          <ul class="subtitle-list">
            <li
              v-for="s in currentSubtitles"
              :key="s.id"
              :class="['subtitle-item', { active: s.id === currentSubtitleId }]"
              @click="seekTo(s.start)"
            >
              <div class="time">{{ formatTime(s.start) }}</div>
              <div class="text">
                <div>{{ s.text }}</div>
                <div v-if="s.textCn" class="text-cn">{{ s.textCn }}</div>
              </div>
            </li>
          </ul>
        </div>

        <!-- Tab2：单词 -->
        <div v-else-if="activeTab === 'words'" class="tab-panel">
          <p class="placeholder">
            这里将展示当前视频中的单词列表（来源词库 + 收藏按钮）。目前为占位内容。
          </p>
        </div>

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
        <div v-else-if="activeTab === 'notes'" class="tab-panel">
          <div class="notes-input">
            <textarea
              v-model="newNoteText"
              class="notes-textarea"
              rows="3"
              placeholder="在当前时间记一条笔记，例如听不懂的句子、自己想到的问题……"
            ></textarea>
            <button class="notes-add-btn" @click="addNoteAtCurrentTime" :disabled="!newNoteText.trim()">
              在 {{ formatTimeShort(position) }} 处添加笔记
            </button>
          </div>

          <div class="notes-list-wrap">
            <div v-if="notes.length === 0" class="notes-empty">
              还没有笔记。播放到有疑问的地方时，在上方输入框写下你的想法，然后点击「添加笔记」。
            </div>
            <ul v-else class="notes-list">
              <li v-for="n in notes" :key="n.id" class="note-item">
                <button class="note-time" @click="seekToNote(n.time)">
                  {{ formatTimeShort(n.time) }}
                </button>
                <div class="note-text">
                  {{ n.text }}
                </div>
                <button class="note-delete" @click="removeNote(n.id)">删除</button>
              </li>
            </ul>
          </div>
        </div>

        <!-- Tab6：本视频相关卡片 -->
        <div v-else-if="activeTab === 'cards'" class="tab-panel">
          <p class="placeholder">
            这里将展示从该视频生成的学习卡片，可以直接进入复习或编辑。
          </p>
        </div>
      </div>
    </section>

    <!-- 单词解释浮层（占位） -->
    <div v-if="wordPopup.visible" class="word-popup" :style="wordPopupStyle">
      <div class="word-popup-word">{{ wordPopup.word }}</div>
      <div class="word-popup-brief">这里将展示该单词的释义、音标、例句等。</div>
      <button class="word-popup-btn" @click="onCollectWord">收藏为卡片</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useVideosStore } from '../store/videos';
import { useSubtitlesStore } from '../store/subtitles';
import { useNotesStore } from '../store/notes';

const route = useRoute();
const router = useRouter();
const videosStore = useVideosStore();
const subtitlesStore = useSubtitlesStore();
const notesStore = useNotesStore();

const videoRef = ref<HTMLVideoElement | null>(null);
const activeTab = ref<'subtitles' | 'words' | 'phrases' | 'grammar' | 'notes' | 'cards'>(
  'subtitles',
);
const currentVideoId = computed(() => route.params.id as string | undefined);


// tabs 配置
const tabs = [
  { key: 'subtitles', label: '滚动字幕' },
  { key: 'words', label: '单词' },
  { key: 'phrases', label: '短语 / 俚语' },
  { key: 'grammar', label: '长难句语法' },
  { key: 'notes', label: '笔记 / 标注' },
  { key: 'cards', label: '本视频卡片' },
];

// 当前视频
const currentVideo = computed(() => {
  const id = currentVideoId.value;
  if (!id) return null;
  return videosStore.items.find((v) => v.id === id) ?? null;
});

// 当前视频的笔记列表
const notes = computed(() => {
  const id = currentVideoId.value;
  if (!id) return [];
  return notesStore.notesForVideo(id);
});


// 先用一个假 src，占位用
const videoSrc = computed(() => {
  // 真实项目中应从 currentVideo.filePath 或后端地址获取
  return '';
});

const newNoteText = ref('');

// 播放进度 & 时长（简单占位）
const position = ref(0);
const duration = ref(0);

const positionDisplay = computed(() => formatTime(position.value));
const durationDisplay = computed(() => (duration.value ? formatTime(duration.value) : '--:--'));

const currentSubtitles = computed(() => {
  const id = currentVideoId.value;
  if (!id) return [] as ReturnType<typeof subtitlesStore.subtitlesForVideo>;
  return subtitlesStore.subtitlesForVideo(id);
});

// 根据播放时间找到当前句
const currentSubtitleId = computed(() => {
  const t = position.value;
  const s = currentSubtitles.value.find((x) => t >= x.start && t < x.end);
  return s?.id ?? null;
});

const currentSubtitle = computed(() => {
  return currentSubtitles.value.find((s) => s.id === currentSubtitleId.value) ?? null;
});

const currentSubtitleWords = computed(() => {
  if (!currentSubtitle.value) return [];
  return currentSubtitle.value.text.split(' ');
});

// 单词解释弹层
const wordPopup = reactive({
  visible: false,
  word: '',
  x: 0,
  y: 0,
});

const wordPopupStyle = computed(() => ({
  left: `${wordPopup.x}px`,
  top: `${wordPopup.y}px`,
}));

function onTimeUpdate() {
  if (!videoRef.value) return;
  position.value = videoRef.value.currentTime;
}

function onLoadedMetadata() {
  if (!videoRef.value) return;
  duration.value = videoRef.value.duration;
}

function seekTo(t: number) {
  if (!videoRef.value) return;
  videoRef.value.currentTime = t;
  videoRef.value.play();
}

function goBackToVideos() {
  router.push({ name: 'videos' });
}

function onWordClick(word: string, event?: MouseEvent) {
  wordPopup.word = word.replace(/[.,!?]/g, '');
  wordPopup.visible = true;
  if (event) {
    wordPopup.x = event.clientX + 10;
    wordPopup.y = event.clientY - 40;
  } else {
    wordPopup.x = 200;
    wordPopup.y = 200;
  }
}

function onCollectWord() {
  // TODO: 调用卡片创建逻辑
  alert(`将来这里会把单词「${wordPopup.word}」收藏成一张学习卡片。`);
  wordPopup.visible = false;
}

// 点击其它地方关闭单词弹层
function onClickDocument(e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (target.closest('.word-popup') || target.closest('.subtitle-bar')) return;
  wordPopup.visible = false;
}

function addNoteAtCurrentTime() {
  const id = currentVideoId.value;
  if (!id || !videoRef.value) return;
  const text = newNoteText.value.trim();
  if (!text) return;
  notesStore.addNote({
    videoId: id,
    time: videoRef.value.currentTime,
    text,
  });
  newNoteText.value = '';
}

function seekToNote(time: number) {
  if (!videoRef.value) return;
  videoRef.value.currentTime = time;
  videoRef.value.play();
}

function removeNote(noteId: string) {
  const id = currentVideoId.value;
  if (!id) return;
  if (!confirm('确定要删除这条笔记吗？')) return;
  notesStore.removeNote(id, noteId);
}

function formatTimeShort(sec: number) {
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const ss = s % 60;
  return `${m.toString().padStart(2, '0')}:${ss.toString().padStart(2, '0')}`;
}




onMounted(() => {
  // 绑定 video 事件
  if (videoRef.value) {
    videoRef.value.addEventListener('timeupdate', onTimeUpdate);
    videoRef.value.addEventListener('loadedmetadata', onLoadedMetadata);
  }
  document.addEventListener('click', onClickDocument);

  // 开发阶段：为当前视频自动填充假字幕
  const id = currentVideoId.value;
  if (id) {
    subtitlesStore.seedMockForVideo(id);
  }
});

onUnmounted(() => {
  if (videoRef.value) {
    videoRef.value.removeEventListener('timeupdate', onTimeUpdate);
    videoRef.value.removeEventListener('loadedmetadata', onLoadedMetadata);
  }
  document.removeEventListener('click', onClickDocument);
});

function formatTime(sec: number | undefined) {
  if (!sec && sec !== 0) return '--:--';
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const ss = s % 60;
  return `${m.toString().padStart(2, '0')}:${ss.toString().padStart(2, '0')}`;
}
</script>

<style scoped>
.player-page {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2.2fr);
  gap: 16px;
  height: 100%;
}

/* 左侧 */
.left {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.video-wrapper {
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 10px;
}

.video {
  width: 100%;
  height: 360px;
  background: #000;
}

/* 底部字幕条 */
.subtitle-bar {
  margin-top: auto;
  padding: 8px 10px;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.9);
  color: #f9fafb;
  font-size: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.subtitle-word {
  cursor: pointer;
}

.subtitle-word:hover {
  text-decoration: underline;
}

/* 右侧 */
.right {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.right-header {
  display: flex;
  justify-content: space-between;
  align-items: center; /* 原本是 baseline，可以改成 center，看你喜好 */
  margin-bottom: 8px;
}

.right-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn {
  border: 1px solid #d1d5db;
  background: #ffffff;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
  color: #374151;
}

.back-btn:hover {
  background: #f3f4f6;
}

.right-header .title {
  font-size: 16px;
  font-weight: 500;
}

.right-header .time {
  font-size: 12px;
  color: #6b7280;
}

.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.tab {
  padding: 6px 10px;
  font-size: 13px;
  border-radius: 999px;
  border: none;
  background: #e5e7eb;
  cursor: pointer;
}

.tab.active {
  background: #2563eb;
  color: #ffffff;
}

.tab-content {
  flex: 1;
  padding: 8px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  overflow: auto;
}

.placeholder {
  font-size: 13px;
  color: #6b7280;
}

/* 滚动字幕列表 */
.subtitle-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.subtitle-item {
  display: grid;
  grid-template-columns: 60px minmax(0, 1fr);
  gap: 8px;
  padding: 6px 4px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.subtitle-item:hover {
  background: #f3f4f6;
}

.subtitle-item.active {
  background: #dbeafe;
}

.subtitle-item .time {
  color: #6b7280;
  font-variant-numeric: tabular-nums;
}

/* 单词浮层 */
.word-popup {
  position: fixed;
  z-index: 50;
  min-width: 200px;
  max-width: 260px;
  background: #111827;
  color: #f9fafb;
  border-radius: 8px;
  padding: 8px 10px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.45);
  font-size: 13px;
}

.word-popup-word {
  font-weight: 600;
  margin-bottom: 4px;
}

.word-popup-brief {
  color: #d1d5db;
  margin-bottom: 6px;
}

.word-popup-btn {
  border: none;
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 999px;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
}

.subtitle-item .text-cn {
  font-size: 12px;
  color: #6b7280;
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
  color: #6b7280;
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
  background: #f9fafb;
}

.note-time {
  border-radius: 999px;
  border: none;
  background: #e5e7eb;
  padding: 2px 8px;
  font-size: 12px;
  cursor: pointer;
  font-variant-numeric: tabular-nums;
}

.note-text {
  font-size: 13px;
  color: #111827;
}

.note-delete {
  border: none;
  background: transparent;
  color: #ef4444;
  font-size: 12px;
  cursor: pointer;
}
</style>