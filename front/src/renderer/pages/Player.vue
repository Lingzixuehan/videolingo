<template>
  <div class="player-page">
    <!-- 左侧：视频 + 底部字幕 -->
    <section class="left">
      <div class="video-wrapper">
        <video
          ref="videoRef"
          class="video"
          controls
          muted
          autoplay
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
                    @click="seekTo(c.videoTime!)"
                  >
                    跳到 {{ formatTimeShort(c.videoTime!) }}
                  </button>
                  <span v-if="c.videoTitle" class="video-card-title">{{ c.videoTitle }}</span>
                </div>
              </div>
              <div class="video-card-actions">
                <button class="video-card-btn" @click="goToReview">去复习</button>
                <button class="video-card-btn delete" @click="deleteCard(c.id)">删除</button>
              </div>
            </li>
          </ul>
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
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCardsStore } from '../store/cards';
import { useNotesStore } from '../store/notes';
import { useSubtitlesStore } from '../store/subtitles';
import { useVideosStore } from '../store/videos';

const route = useRoute();
const router = useRouter();
const videosStore = useVideosStore();
const subtitlesStore = useSubtitlesStore();
const notesStore = useNotesStore();
const cardsStore = useCardsStore();
const subtitleItemRefs = ref<Record<string, HTMLLIElement | null>>({});

const isMockTiming = import.meta.env.DEV; // 只在 dev 下用假时间轴
let mockTimer: number | null = null;


const videoRef = ref<HTMLVideoElement | null>(null);

const activeTab = ref<'subtitles' | 'words' | 'phrases' | 'grammar' | 'notes' | 'cards'>(
  'subtitles',
);
const currentVideoId = computed(() => route.params.id as string | undefined);
const currentVideo = computed(() =>
  currentVideoId.value
    ? videosStore.items.find(v => v.id === currentVideoId.value) ?? null
    : null
);

// 本视频相关卡片
const videoCards = computed(() => {
  const id = currentVideoId.value;
  if (!id) return [];
  return cardsStore.itemsAll.filter((c) => c.videoId === id);
});
// tabs 配置
const tabs = [
  { key: 'subtitles', label: '滚动字幕' },
  { key: 'words', label: '单词' },
  { key: 'phrases', label: '短语 / 俚语' },
  { key: 'grammar', label: '长难句语法' },
  { key: 'notes', label: '笔记 / 标注' },
  { key: 'cards', label: '本视频卡片' },
];

// 用于网络环境下的演示视频（备用）
const fallbackVideoSrc = 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4';

const videoSrc = computed(() => {
  const v = currentVideo.value;
  const serverBase = 'http://127.0.0.1:3421';

  // 情况 1：有 filePath（本地或相对）
  if (v?.filePath) {
    try {
      // Use the local video-server to stream files with Range support
      return `${serverBase}/video?path=${encodeURIComponent(v.filePath)}`;
    } catch (e) {
      console.warn('[Player] encode video path fail', e);
    }
  }

  // 情况 2：暂时没有有效 filePath 时，使用内置示例 test.mp4（通过 video-server）
  return `${serverBase}/video?path=${encodeURIComponent('/public/videos/test.mp4')}`;
});

// 当前视频的笔记列表
const notes = computed(() => {
  const id = currentVideoId.value;
  if (!id) return [];
  return notesStore.notesForVideo(id);
});

const newNoteText = ref('');

// 播放进度 & 时长
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

function goToReview() {
  router.push({ name: 'study-review' });
}

function onWordClick(word: string, event?: MouseEvent) {
  const cleanWord = word.replace(/[.,!?]/g, '');

  wordPopup.word = cleanWord;
  wordPopup.visible = true;
  
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  wordPopup.x = vw / 2;
  wordPopup.y = vh / 2;
}



function onCollectWord() {
  const word = wordPopup.word.trim();
  if (!word) return;

  const videoId = currentVideoId.value ?? '';
  const videoTitle = currentVideo.value?.title ?? '';

  cardsStore.addFromVideo({
    wordOrSentence: word,
    meaning: '',
    type: 'word',
    videoId,
    videoTitle,
    videoTime: position.value,
  });

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

function deleteCard(id: string) {
  if (!confirm('确定要删除这张卡片吗？')) return;
  cardsStore.removeById(id);
}

function formatTimeShort(sec: number) {
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const ss = s % 60;
  return `${m.toString().padStart(2, '0')}:${ss.toString().padStart(2, '0')}`;
}

function setSubtitleItemRef(el: HTMLLIElement | null, id: string) {
  if (!el) return;
  subtitleItemRefs.value[id] = el;
}



onMounted(() => {
  if (videoRef.value) {
    const el = videoRef.value;
    el.addEventListener('loadedmetadata', () => {
      console.log('[Player] loadedmetadata duration =', el.duration);
    });
    el.addEventListener('error', () => {
      console.log('[Player] video error', el.error);
    });
    el.addEventListener('play', () => {
      console.log('[Player] play event fired');
    });

        // 尝试主动播放一次
    const p = el.play();
    if (p && typeof p.then === 'function') {
      p.then(() => {
        console.log('[Player] play() resolved');
      }).catch(err => {
        console.log('[Player] play() rejected', err);
      });
    }
  }



  const video = videoRef.value;
  if (video) {
    video.addEventListener('timeupdate', onTimeUpdate);
    video.addEventListener('loadedmetadata', onLoadedMetadata);
  }
  document.addEventListener('click', onClickDocument);

  const id = currentVideoId.value;
  if (id) {
    subtitlesStore.seedMockForVideo(id);
  }

  // dev 下：不依赖真实视频，直接用 0~120 秒的假时间轴驱动字幕
  if (isMockTiming) {
    duration.value = 120;
    position.value = 0;
    mockTimer = window.setInterval(() => {
      position.value = (position.value + 0.5) % duration.value;
    }, 500);
  }
});

onUnmounted(() => {
  const video = videoRef.value;
  if (video) {
    video.removeEventListener('timeupdate', onTimeUpdate);
    video.removeEventListener('loadedmetadata', onLoadedMetadata);
  }
  document.removeEventListener('click', onClickDocument);

  if (mockTimer !== null) {
    clearInterval(mockTimer);
    mockTimer = null;
  }
});

watch(currentSubtitleId, (id) => {
  if (!id) return;
  const el = subtitleItemRefs.value[id];
  if (!el) return;
  const container = el.closest('.subtitle-list');
  if (!container) return;

  const rect = el.getBoundingClientRect();
  const crect = (container as HTMLElement).getBoundingClientRect();
  const offset = rect.top - crect.top - crect.height / 3;
  (container as HTMLElement).scrollBy({ top: offset, behavior: 'smooth' });
});


function formatTime(sec: number | undefined) {
  if (!sec && sec !== 0) return '--:--';
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const ss = s % 60;
  return `${m.toString().padStart(2, '0')}:${ss.toString().padStart(2, '0')}`;
}

function addWordCard(word: string, meaning: string | undefined, time: number) {
  cardsStore.addFromVideo({
    wordOrSentence: word,
    meaning,
    type: 'word',
    videoId: currentVideoId.value,
    videoTitle: currentVideo.value?.title,
    videoTime: time,
  });
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
  height: 420px;
  background: #000;
}

/* 底部字幕条 */
  .subtitle-bar {
    margin-top: auto;
    padding: 10px 14px;
    border-radius: 8px;
    background: rgba(10, 16, 28, 0.85);
    color: var(--c-text);
    font-size: 16px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .subtitle-word {
    cursor: pointer;
    padding: 2px 6px;
    border-radius: 6px;
    background: rgba(255,255,255,0.02);
    transition: background .12s ease, color .12s ease;
  }

  .subtitle-word:hover {
    background: rgba(56,189,248,0.14);
    color: #fff;
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

/* 本视频卡片列表 */
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

/* 滚动字幕列表 */
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

/* 单词浮层 */
.word-popup {
  position: fixed;
  z-index: 9999;
  min-width: 320px;
  max-width: 420px;
  background: #ffffff;
  color: #111827;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.35);
  font-size: 14px;
  transform: translate(-50%, -50%);
}

.word-popup-word {
  font-weight: 700;
  font-size: 22px;
  margin-bottom: 8px;
}

.word-popup-brief {
  color: #6b7280;
  margin-bottom: 12px;
  font-size: 13px;
}

.word-popup-btn {
  border: none;
  padding: 6px 12px;
  font-size: 13px;
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