<template>
  <div class="wrap">
    <h2>概览</h2>
    <div class="stats">
      <div class="card">
        <span>视频数</span>
        <strong>{{ videos.count }}</strong>
      </div>
      <div class="card">
        <span>进行中任务</span>
        <strong>{{ tasks.active.length }}</strong>
      </div>
      <div class="card">
        <span>当前用户</span>
        <strong>{{ user.displayName }}</strong>
      </div>
    </div>
    <div class="quick">
      <button @click="go('/videos')">添加视频</button>
      <button @click="go('/tasks')">查看任务</button>
      <button @click="go('/subtitles')">字幕编辑</button>
      <button @click="go('/review')">复习</button>
      <button @click="go('/analyze')">分析</button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useVideosStore } from '../store/videos';
import { useTasksStore } from '../store/tasks';
import { useUserStore } from '../store/user';
const router = useRouter();
const videos = useVideosStore();
const tasks = useTasksStore();
const user = useUserStore();
function go(p:string){ router.push(p); }
</script>
<style scoped>
.wrap { padding:16px; }
.stats { display:flex; gap:12px; flex-wrap:wrap; margin:12px 0 20px; }
.card { background:#fff; border:1px solid #e5e7eb; border-radius:6px; padding:12px 16px; min-width:140px; }
.card span { display:block; font-size:12px; color:#666; }
.card strong { font-size:22px; }
.quick button { margin:0 8px 8px 0; }
</style>