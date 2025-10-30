<template>
  <div class="page">
    <h2>播放器</h2>
    <button @click="pick">选择本地视频</button>
    <p v-if="filePath">已选择: {{ filePath }}</p>
    <video v-if="filePath" :src="videoSrc" controls style="width:100%;max-width:960px;margin-top:12px;"></video>
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue';
const filePath = ref<string>('');
const videoSrc = computed(() => (filePath.value ? `file://${filePath.value}` : ''));
async function pick() {
  const res = await window.api?.pickVideo?.();
  if (res?.canceled === false && res.filePaths?.length) filePath.value = res.filePaths[0];
}
</script>