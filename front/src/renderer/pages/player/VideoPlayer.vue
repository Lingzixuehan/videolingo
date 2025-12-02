<template>
  <section class="left">
    <div class="video-wrapper">
      <video
        ref="videoRef"
        class="video"
        controls
        muted
        :src="src"
        @error="onVideoElementError"
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onLoadedMetadata"
        @play="onPlay"
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
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';

const props = defineProps<{
  src: string;
  currentSubtitle: { text: string } | null;
}>();

const emit = defineEmits<{
  (e: 'update:currentTime', time: number): void;
  (e: 'update:duration', duration: number): void;
  (e: 'wordClick', word: string, event: MouseEvent): void;
}>();

const videoRef = ref<HTMLVideoElement | null>(null);
const triedFallback = ref<Record<string, boolean>>({});

const currentSubtitleWords = computed(() => {
  if (!props.currentSubtitle) return [];
  return props.currentSubtitle.text.split(' ');
});

function onTimeUpdate() {
  if (!videoRef.value) return;
  emit('update:currentTime', videoRef.value.currentTime);
}

function onLoadedMetadata() {
  if (!videoRef.value) return;
  emit('update:duration', videoRef.value.duration);
}

function onPlay() {
  console.log('[VideoPlayer] play event fired');
}

function onWordClick(word: string, event: MouseEvent) {
  emit('wordClick', word, event);
}

// Expose methods for parent control
function seek(time: number) {
  if (!videoRef.value) return;
  videoRef.value.currentTime = time;
  videoRef.value.play();
}

function play() {
  videoRef.value?.play();
}

function pause() {
  videoRef.value?.pause();
}

defineExpose({
  seek,
  play,
  pause,
  videoElement: videoRef
});

// Video loading logic
async function tryLoadVideo() {
  const el = videoRef.value;
  if (!el) return;

  const src = props.src;
  console.log('[VideoPlayer] tryLoadVideo ->', src);

  // Reset any existing object URL
  if (el.src && el.src.startsWith('blob:')) {
    try { URL.revokeObjectURL(el.src); } catch (e) {}
  }

  // Set src and attempt to play
  try {
    el.src = src;
    el.load();
    const p = el.play();
    if (p && typeof p.then === 'function') {
      await p;
      console.log('[VideoPlayer] play() succeeded');
    }
  } catch (err) {
    console.warn('[VideoPlayer] initial play() error', err);
  }
}

async function onVideoElementError(e?: Event) {
  const el = videoRef.value;
  if (!el) return;
  const src = props.src;
  console.warn('[VideoPlayer] video element error, attempting fetch fallback', src, e);

  if (triedFallback.value[src]) {
    console.warn('[VideoPlayer] fallback already attempted for this src, will not retry:', src);
    return;
  }

  try {
    const resp = await fetch(src);
    if (!resp.ok) throw new Error('fetch failed: ' + resp.status);
    const blob = await resp.blob();
    const blobUrl = URL.createObjectURL(blob);
    triedFallback.value[src] = true;
    el.src = blobUrl;
    el.load();
    await el.play().catch(err => console.warn('[VideoPlayer] play after blob failed', err));
    console.log('[VideoPlayer] playback started using blob fallback');
  } catch (err) {
    console.error('[VideoPlayer] blob fallback failed', err);
  }
}

watch(() => props.src, () => {
  tryLoadVideo().catch(err => console.warn('[VideoPlayer] tryLoadVideo on change failed', err));
});

onMounted(() => {
  if (props.src) {
    tryLoadVideo().catch(err => console.warn('[VideoPlayer] tryLoadVideo failed', err));
  }
});
</script>

<style scoped>
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
</style>
