<template>
  <div class="review-page">
    <!-- 顶部信息栏 -->
    <header class="top">
      <div class="left">
        <div class="title">今日复习</div>
        <div class="sub">
          目标 {{ cardsStore.todayTarget }} 张 · 已完成 {{ cardsStore.doneCount }} 张 · 剩余
          {{ cardsStore.remainingCount }} 张
        </div>
      </div>
      <div class="right">
        <div class="index">
          {{ displayIndex }} / {{ totalCount }}
        </div>
        <button class="restart-btn" @click="onRestart" :disabled="!totalCount">
          重置今日进度
        </button>
      </div>
    </header>

    <!-- 主体：大卡片 -->
    <main class="main">
      <div v-if="!currentCard" class="empty">
        <p>今天还没有可复习的卡片。</p>
        <p>后续会从你收藏的单词、句子和笔记中自动生成复习队列。</p>
      </div>

      <div v-else class="card">
        <div class="card-type">{{ typeLabel }}</div>
        <div class="card-front" v-if="!showBack">
          {{ currentCard.front }}
        </div>
        <div class="card-back" v-else>
          {{ currentCard.back }}
        </div>

        <div class="card-source" v-if="currentCard.videoTitle">
          <span>来源视频：</span>
          <span class="link" @click="goToSource"> {{ currentCard.videoTitle }} </span>
          <span v-if="currentCard.videoTime">
            · {{ formatTime(currentCard.videoTime) }}
          </span>
        </div>

        <div class="card-actions">
          <button class="flip-btn" @click="toggleShowBack">
            {{ showBack ? '返回题目 (Space)' : '显示答案 (Space)' }}
          </button>
        </div>
      </div>
    </main>

    <!-- 底部反馈按钮 -->
    <footer class="bottom" v-if="currentCard">
      <button class="btn hard" @click="answer('hard')">困难 (1)</button>
      <button class="btn normal" @click="answer('normal')">一般 (2)</button>
      <button class="btn easy" @click="answer('easy')">简单 (3)</button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useCardsStore } from '../store/cards';

const cardsStore = useCardsStore();
const router = useRouter();

const showBack = ref(false);

// 初始化今日卡片（假数据）
onMounted(() => {
  cardsStore.seedMockToday();
  window.addEventListener('keydown', onKeyDown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeyDown);
});

const currentCard = computed(() => cardsStore.currentCard);
const totalCount = computed(() => cardsStore.itemsToday.length);
const displayIndex = computed(() =>
  currentCard.value ? cardsStore.currentIndex + 1 : 0,
);

const typeLabel = computed(() => {
  switch (currentCard.value?.type) {
    case 'word':
      return '单词卡';
    case 'phrase':
      return '短语卡';
    case 'sentence':
      return '句子卡';
    case 'grammar':
      return '语法卡';
    case 'note':
      return '笔记卡';
    default:
      return '卡片';
  }
});

function toggleShowBack() {
  if (!currentCard.value) return;
  showBack.value = !showBack.value;
}

function answer(ease: 'hard' | 'normal' | 'easy') {
  if (!currentCard.value) return;
  cardsStore.answerCurrent(ease);
  showBack.value = false;
}

function onRestart() {
  cardsStore.restartToday();
  showBack.value = false;
}

function goToSource() {
  const card = currentCard.value;
  if (!card?.videoId) return;
  router.push({ name: 'player', params: { id: card.videoId } });
}

function formatTime(sec: number) {
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const ss = s % 60;
  return `${m.toString().padStart(2, '0')}:${ss.toString().padStart(2, '0')}`;
}

// 键盘快捷键：Space 翻面；1/2/3 选择困难/一般/简单
function onKeyDown(e: KeyboardEvent) {
  if (!currentCard.value) return;
  if (e.code === 'Space') {
    e.preventDefault();
    toggleShowBack();
  } else if (e.key === '1') {
    e.preventDefault();
    answer('hard');
  } else if (e.key === '2') {
    e.preventDefault();
    answer('normal');
  } else if (e.key === '3') {
    e.preventDefault();
    answer('easy');
  }
}
</script>

<style scoped>
.review-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 顶部 */
.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.title {
  font-size: 18px;
  font-weight: 500;
}

.sub {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.index {
  font-size: 13px;
  color: #4b5563;
}

.restart-btn {
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
}

.restart-btn:disabled {
  opacity: 0.5;
  cursor: default;
}

/* 中间卡片 */
.main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty {
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}

.card {
  width: 520px;
  min-height: 220px;
  background: #ffffff;
  border-radius: 16px;
  padding: 18px 20px;
  box-shadow: 0 15px 40px rgba(15, 23, 42, 0.12);
  display: flex;
  flex-direction: column;
}

.card-type {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.card-front,
.card-back {
  flex: 1;
  font-size: 18px;
  line-height: 1.6;
  display: flex;
  align-items: center;
}

.card-source {
  font-size: 12px;
  color: #6b7280;
  margin-top: 8px;
}

.card-source .link {
  color: #2563eb;
  cursor: pointer;
}

.card-source .link:hover {
  text-decoration: underline;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.flip-btn {
  border-radius: 999px;
  border: none;
  background: #2563eb;
  color: #ffffff;
  font-size: 13px;
  padding: 6px 16px;
  cursor: pointer;
}

/* 底部按钮 */
.bottom {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 10px;
}

.btn {
  min-width: 96px;
  border-radius: 999px;
  border: none;
  padding: 8px 14px;
  font-size: 14px;
  cursor: pointer;
  color: #fff;
}

.btn.hard {
  background: #ef4444;
}

.btn.normal {
  background: #f59e0b;
}

.btn.easy {
  background: #22c55e;
}
</style>