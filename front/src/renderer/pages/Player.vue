<template>
  <div class="player-page">
    <!-- 左侧：视频 + 底部字幕 -->
    <VideoPlayer
      ref="videoPlayerRef"
      :src="videoSrc"
      :currentSubtitle="currentSubtitle"
      @update:currentTime="onTimeUpdate"
      @update:duration="onDurationUpdate"
      @wordClick="onWordClick"
    />

    <!-- 右侧：Tab 区域 -->
    <PlayerSidebar
      :title="currentVideo?.title || '未选择视频'"
      :position="position"
      :duration="duration"
      :whisperProcessing="whisperProcessing"
      :extractProgress="extractProgress"
      v-model:activeTab="activeTab"
      :subtitles="currentSubtitles"
      :currentSubtitleId="currentSubtitleId"
      :wordLabels="wordLabels"
      :notes="notes"
      :videoCards="videoCards"
      @back="goBackToVideos"
      @extract="startExtract"
      @translate="startTranslateAndEmbed"
      @analyze="onAnalyze"
      @seek="seekTo"
      @addCard="addWordCard"
      @addNote="addNote"
      @removeNote="removeNote"
      @review="goToReview"
      @deleteCard="deleteCard"
    />

    <!-- 单词解释浮层 -->
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
import { useCardsStore } from '../store/cards';
import { useNotesStore } from '../store/notes';
import { useSubtitlesStore } from '../store/subtitles';
import { useVideosStore } from '../store/videos';
import { useWhisperMock } from '../composables/useWhisperMock';

import VideoPlayer from './player/VideoPlayer.vue';
import PlayerSidebar from './player/PlayerSidebar.vue';

const route = useRoute();
const router = useRouter();
const videosStore = useVideosStore();
const subtitlesStore = useSubtitlesStore();
const notesStore = useNotesStore();
const cardsStore = useCardsStore();

const videoPlayerRef = ref<InstanceType<typeof VideoPlayer> | null>(null);

const currentVideoId = computed(() => route.params.id as string | undefined);
const currentVideo = computed(() =>
  currentVideoId.value
    ? videosStore.items.find(v => v.id === currentVideoId.value) ?? null
    : null
);

// Video Source Logic
const videoSrc = computed(() => {
  const v = currentVideo.value;
  if (!v?.filePath) {
    try {
      return new URL('../../common/whisper/examples/input.mp4', import.meta.url).href;
    } catch (e) {
      console.warn('[Player] example video URL mapping failed', e);
      return `app://video/${encodeURIComponent('test.mp4')}`;
    }
  }

  const p = String(v.filePath);
  if (p.startsWith('app://') || p.startsWith('file://')) return p;

  try {
    const isHttpOrigin = typeof window !== 'undefined' && window.location && /^https?:/.test(window.location.protocol);
    if (import.meta.env.DEV) {
      const rel = p.replace(/^\\\\|^\//, '').replace(/^public\//, '').replace(/^videos\//, 'videos/');
      return `http://127.0.0.1:3421/${rel}`;
    }
    if (isHttpOrigin) {
      const publicMatch = p.replace(/^\\\\|^\//, '').match(/^public\/(.*)/);
      if (publicMatch) return `${window.location.origin}/${publicMatch[1]}`;
      const videosMatch = p.replace(/^\\\\|^\//, '').match(/^videos\/(.*)/);
      if (videosMatch) return `${window.location.origin}/${p.replace(/^\\/,'')}`;
    }
  } catch (e) {
    console.warn('[Player] dev mapping check failed', e);
  }

  try {
    if (/^[a-zA-Z]:[\\/]/.test(p) || p.startsWith('/')) {
      return encodeURI('file:///' + p.replace(/\\/g, '/'));
    }
  } catch (e) {
    console.warn('[Player] detect absolute path failed', e);
  }

  try {
    const parts = p.split(/[/\\]/);
    const fileName = parts[parts.length - 1] || p;
    return `app://video/${encodeURIComponent(fileName)}`;
  } catch (e) {
    return `app://video/${encodeURIComponent('test.mp4')}`;
  }
});

// Helper for Whisper Mock
function getLocalVideoPath(): string | null {
  let p = currentVideo.value?.filePath;
  if (!p) {
    try {
      return new URL('../../common/whisper/examples/input.mp4', import.meta.url).href;
    } catch (e) {
      return './public/videos/test.mp4';
    }
  }
  try {
    if (p.startsWith('app://')) {
      const url = new URL(p);
      const fileName = decodeURIComponent(url.pathname.replace(/^\//, ''));
      return `./public/videos/${fileName}`;
    }
    if (p.startsWith('file://')) {
      return decodeURIComponent(p.replace(/^file:\/\//, ''));
    }
    return p;
  } catch (e) {
    return p;
  }
}

// Whisper Mock Logic
const {
  whisperProcessing,
  extractProgress,
  wordLabels,
  startExtract,
  startTranslateAndEmbed,
  startAnalyzeAndLabel
} = useWhisperMock(currentVideoId, getLocalVideoPath);

async function onAnalyze() {
  const success = await startAnalyzeAndLabel();
  if (success) {
    activeTab.value = 'words';
  }
}

// Player State
const position = ref(0);
const duration = ref(0);
const activeTab = ref('subtitles');

const currentSubtitles = computed(() => {
  const id = currentVideoId.value;
  if (!id) return [];
  return subtitlesStore.subtitlesForVideo(id);
});

const currentSubtitleId = computed(() => {
  const t = position.value;
  const s = currentSubtitles.value.find((x) => t >= x.start && t < x.end);
  return s?.id ?? null;
});

const currentSubtitle = computed(() => {
  return currentSubtitles.value.find((s) => s.id === currentSubtitleId.value) ?? null;
});

const notes = computed(() => {
  const id = currentVideoId.value;
  if (!id) return [];
  return notesStore.notesForVideo(id);
});

const videoCards = computed(() => {
  const id = currentVideoId.value;
  if (!id) return [];
  return cardsStore.itemsAll.filter((c) => c.videoId === id);
});

// Methods
function onTimeUpdate(time: number) {
  position.value = time;
}

function onDurationUpdate(d: number) {
  duration.value = d;
}

function seekTo(time: number) {
  videoPlayerRef.value?.seek(time);
}

function goBackToVideos() {
  router.push({ name: 'videos' });
}

function goToReview() {
  router.push({ name: 'study-review' });
}

function addNote(text: string, time: number) {
  const id = currentVideoId.value;
  if (!id) return;
  notesStore.addNote({
    videoId: id,
    time,
    text,
  });
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

function addWordCard(word: string, meaning: string) {
  cardsStore.addFromVideo({
    wordOrSentence: word,
    meaning,
    type: 'word',
    videoId: currentVideoId.value,
    videoTitle: currentVideo.value?.title,
    videoTime: position.value,
  });
}

// Word Popup Logic
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

function onWordClick(word: string, event: MouseEvent) {
  const cleanWord = word.replace(/[.,!?]/g, '');
  wordPopup.word = cleanWord;
  wordPopup.visible = true;
  wordPopup.x = window.innerWidth / 2;
  wordPopup.y = window.innerHeight / 2;
}

function onCollectWord() {
  const word = wordPopup.word.trim();
  if (!word) return;
  addWordCard(word, '');
  wordPopup.visible = false;
}

function onClickDocument(e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (target.closest('.word-popup') || target.closest('.subtitle-bar')) return;
  wordPopup.visible = false;
}

onMounted(() => {
  document.addEventListener('click', onClickDocument);
  const id = currentVideoId.value;
  if (id) {
    subtitlesStore.seedMockForVideo(id);
  }
});

onUnmounted(() => {
  document.removeEventListener('click', onClickDocument);
});
</script>

<style scoped>
.player-page {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2.2fr);
  gap: 16px;
  height: 100%;
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
</style>
