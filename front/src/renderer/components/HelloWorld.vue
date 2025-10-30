<template>
  <div class="hello">
    <h1>VideoLingo 客户端</h1>
    <p>Electron + Vue 3 + TypeScript 已运行。</p>
    <p>Electron 版本: {{ versions.electron }}</p>
    <button @click="ping">Ping 主进程</button>
    <p v-if="pong">收到: {{ pong }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const pong = ref('');
const versions = (window as any).versions ?? { electron: 'unknown' };

async function ping() {
  const res = await (window as any).api?.ping?.();
  pong.value = String(res ?? 'no preload api');
}
</script>