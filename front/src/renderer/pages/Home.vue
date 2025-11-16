<template>
  <div class="wrap">
    <h2>概览</h2>
    <div class="stats">
      <StatCard label="视频数" :value="videos.count" />
      <StatCard label="进行中任务" :value="tasks.active.length" />
      <StatCard label="当前用户" :value="user.displayName || '--'" />
    </div>
    <div class="quick">
      <BaseButton variant="primary" @click="go('/videos')">添加视频</BaseButton>
      <BaseButton @click="go('/tasks')">查看任务</BaseButton>
      <BaseButton @click="go('/subtitles')">字幕编辑</BaseButton>
      <BaseButton @click="go('/review')">复习</BaseButton>
      <BaseButton @click="go('/analyze')">分析</BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useVideosStore } from '../store/videos';
import { useTasksStore } from '../store/tasks';
import { useUserStore } from '../store/user';
import BaseButton from '../components/BaseButton.vue';
import StatCard from '../components/StatCard.vue';

const router = useRouter();
const videos = useVideosStore();
const tasks = useTasksStore();
const user = useUserStore();

function go(path: string) {
  router.push(path);
}
</script>

<style scoped>
.wrap {
  padding: 4px;
}
h2 {
  margin: 0 0 16px;
}
.stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}
.quick {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>