<template>
  <div class="wrap">
    <h2>本地视频</h2>

    <div class="uploader">
      <input ref="fileInput" type="file" accept="video/*" multiple @change="onFiles" />
      <button @click="choose">选择视频文件</button>
      <small class="hint">限制：≤ 500MB，≤ 20 分钟</small>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="list.length === 0" class="empty">暂无视频，点击“选择视频文件”添加</div>

    <ul v-else class="list">
      <li v-for="v in list" :key="v.id" class="item">
        <div class="meta">
          <div class="name">{{ v.name }}</div>
          <div class="sub">
            <span>{{ formatBytes(v.size) }}</span>
            <span>·</span>
            <span>{{ formatDuration(v.duration) }}</span>
            <span>·</span>
            <span>{{ new Date(v.createdAt).toLocaleString() }}</span>
          </div>
        </div>
        <button class="del" @click="remove(v.id)">删除</button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useVideosStore } from '../store/videos';
import { readVideoMetadata } from '../utils/video';
import { formatBytes, formatDuration } from '../utils/validators';

const fileInput = ref<HTMLInputElement | null>(null);
const store = useVideosStore();

const list = computed(() => store.items);
const error = computed(() => store.error);

onMounted(() => {
  store.load();
});

function choose() {
  store.clearError();
  fileInput.value?.click();
}

async function onFiles(e: Event) {
  store.clearError();
  const input = e.target as HTMLInputElement;
  const files = input.files ? Array.from(input.files) : [];
  for (const f of files) {
    try {
      const { durationSec } = await readVideoMetadata(f);
      store.addFromFile(f, durationSec);
    } catch (err: any) {
      store.error = err?.message || '读取视频信息失败';
    }
  }
  // 清空 input 以便连续选择相同文件
  if (input) input.value = '';
}

function remove(id: string) {
  store.remove(id);
}
</script>

<style scoped>
.wrap { padding: 16px; }
.uploader { display: flex; align-items: center; gap: 12px; margin: 12px 0; }
.uploader input[type="file"] { display: none; }
.hint { color: #666; }
.error { color: #c00; margin: 8px 0; }
.empty { color: #666; margin-top: 12px; }
.list { list-style: none; padding: 0; margin: 12px 0; display: flex; flex-direction: column; gap: 8px; }
.item { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border: 1px solid #e5e7eb; border-radius: 6px; background: #fff; }
.meta .name { font-weight: 600; }
.meta .sub { color: #666; font-size: 12px; display: flex; gap: 6px; }
.del { cursor: pointer; }
</style>