<template>
  <div class="wrap">
    <h2>本地视频</h2>
    <div class="uploader card">
      <input ref="fileInput" type="file" accept="video/*" multiple @change="onFiles" />
      <BaseButton variant="primary" @click="choose">选择视频文件</BaseButton>
      <span class="hint">限制：≤500MB / ≤20分钟</span>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="list.length===0" class="empty card">暂无视频，点击“选择视频文件”添加。</div>
    <div v-else class="table-wrap card">
      <table class="table-reset">
        <thead>
          <tr>
            <th>名称</th>
            <th>大小</th>
            <th>时长</th>
            <th>添加时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in list" :key="v.id">
            <td>{{ v.name }}</td>
            <td>{{ formatBytes(v.size) }}</td>
            <td>{{ formatDuration(v.duration) }}</td>
            <td>{{ new Date(v.createdAt).toLocaleString() }}</td>
            <td><BaseButton small variant="danger" @click="remove(v.id)">删除</BaseButton></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useVideosStore } from '../store/videos';
import { readVideoMetadata } from '../utils/video';
import { formatBytes, formatDuration } from '../utils/validators';
import BaseButton from '../components/BaseButton.vue';
const fileInput = ref<HTMLInputElement|null>(null);
const store = useVideosStore();
const list = computed(()=> store.items);
const error = computed(()=> store.error);
onMounted(()=> store.load());
function choose(){ store.clearError(); fileInput.value?.click(); }
async function onFiles(e: Event) {
  store.clearError();
  const input = e.target as HTMLInputElement;
  const files = input.files ? Array.from(input.files) : [];
  for (const f of files) {
    try {
      const { durationSec } = await readVideoMetadata(f);
      store.addFromFile(f, durationSec);
    } catch (err:any) {
      store.error = err?.message || '读取视频信息失败';
    }
  }
  if (input) input.value = '';
}
function remove(id:string){ store.remove(id); }
</script>
<style scoped>
.wrap { padding:4px; }
h2 { margin:0 0 16px; }
.uploader { display:flex; align-items:center; gap:16px; margin-bottom:16px; }
.uploader input { display:none; }
.hint { font-size:12px; color:var(--c-text-dim); }
.error { color:var(--c-danger); margin:10px 0; }
.empty { padding:28px; text-align:center; }
.table-wrap { overflow-x:auto; }
td, th { white-space:nowrap; }
</style>