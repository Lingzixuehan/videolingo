<template>
  <div class="wrap">
    <section class="welcome surface-card">
      <div>
        <h2 class="welcome-title">你好，{{ user.displayName || '学习者' }}</h2>
        <p class="subtitle">今天也一起从真实视频里学语言吧。</p>
      </div>
      <div class="today-plan">
        <div class="plan-label">今日目标</div>
        <div class="plan-value">
          复习 {{ todayTarget }} 张卡片 · 已完成 {{ todayReviewed }} 张
        </div>
      </div>
    </section>

    <section class="stats">
      <StatCard label="已导入视频" :value="videos.count" />
      <StatCard label="待复习卡片" :value="reviewTodo" />
      <StatCard label="累计学习时长(分钟)" :value="totalMinutes" />
    </section>

    <section class="quick surface-card">
      <BaseButton variant="primary" @click="go('/videos')">上传/管理视频</BaseButton>
      <BaseButton @click="go('/study/review')">开始学习</BaseButton>
      <BaseButton @click="go('/study/cards')">卡片管理</BaseButton>
      <BaseButton @click="go('/settings/plan')">学习计划设置</BaseButton>
    </section>

    <section class="lists">
      <div class="list-block surface-card">
        <h3 class="block-title">最近视频</h3>
        <div v-if="recentVideos.length === 0" class="empty">还没有视频，先去上传一个吧。</div>
        <ul v-else class="list">
          <li v-for="v in recentVideos" :key="v.id" class="list-item">
            <div class="list-main">
              <div class="title">{{ v.title }}</div>
              <div class="meta">上次学习：{{ v.lastViewedAt || '未知' }}</div>
            </div>
            <div class="list-actions">
              <BaseButton size="sm" @click="go(`/player/${v.id}`)">继续学习</BaseButton>
            </div>
          </li>
        </ul>
      </div>

      <div class="list-block surface-card">
        <h3 class="block-title">最近卡片</h3>
        <div class="empty muted">卡片系统还没接上，后续会展示最近生成的学习卡片。</div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import BaseButton from '../components/BaseButton.vue';
import StatCard from '../components/StatCard.vue';
import { useUserStore } from '../store/user';
import { useVideosStore } from '../store/videos';

const router = useRouter();
const videos = useVideosStore();
const user = useUserStore();

// 这些先用假数据 / 简单计算，后面再从真正的学习 store 取
const todayTarget = 20;
const todayReviewed = 0;
const reviewTodo = computed(() => Math.max(todayTarget - todayReviewed, 0));
const totalMinutes = 0;

// 这里用已有视频列表做简单的“最近视频”占位（真实情况应有 lastViewedAt 字段）
const recentVideos = computed(() =>
  videos.items
    .slice()
    .reverse()
    .slice(0, 5),
);

function go(path: string) {
  router.push(path);
}
</script>

<style scoped>
.wrap {
  padding: 6px 6px 10px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.welcome {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 18px;
}

.welcome-title {
  margin: 0;
  font-size: 22px;
  font-weight: 650;
}

.subtitle {
  margin: 4px 0 0;
  color: var(--c-text-dim);
  font-size: 14px;
  font-weight: 500;
}

.today-plan {
  text-align: right;
}

.plan-label {
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--c-text-dim);
}

.plan-value {
  font-size: 15px;
  font-weight: 500;
}

.stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.quick {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.lists {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 1.5fr);
  gap: 16px;
}

.block-title {
  margin: 0 0 10px;
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text-dim);
}

.empty {
  padding: 12px;
  font-size: 14px;
  color: var(--c-text);
  background: rgba(15, 23, 42, 0.9);
  border-radius: var(--radius-md);
}

.empty.muted {
  color: var(--c-text-muted);
}

.list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: radial-gradient(circle at top left, rgba(56, 189, 248, 0.05), transparent 60%),
    rgba(15, 23, 42, 0.9);
  border-radius: var(--radius-md);
  border: 1px solid var(--c-border-subtle);
  margin-bottom: 6px;
}

.list-main .title {
  font-size: 15px;
  font-weight: 500;
}

.list-main .meta {
  font-size: 12px;
  color: var(--c-text-muted);
}

.list-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>