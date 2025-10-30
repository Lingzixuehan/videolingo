<template>
  <div class="page">
    <h2>下载中心</h2>
    <ul>
      <li v-for="d in downloads.list" :key="d.id">
        {{ d.name }} - {{ d.status }} {{ d.progress }}%
      </li>
    </ul>
    <button @click="mock">模拟一个下载任务</button>
  </div>
</template>
<script setup lang="ts">
import { useDownloadsStore } from '../store/downloads';
const downloads = useDownloadsStore();
function mock() {
  downloads.enqueue({ id: Date.now().toString(), name: '示例视频.mp4' });
}
</script>