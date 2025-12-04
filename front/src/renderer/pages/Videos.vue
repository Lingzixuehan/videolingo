<template>
  <div class="videos-page">
    <header class="toolbar">
      <div class="left">
        <BaseButton variant="primary" @click="onAddVideo">添加视频</BaseButton>
      </div>
      <div class="right">
        <input
          v-model="keyword"
          class="search"
          type="text"
          placeholder="按标题搜索视频"
        />
        <select v-model="statusFilter" class="filter">
          <option value="">全部状态</option>
          <option value="idle">未生成字幕</option>
          <option value="processing">生成中</option>
          <option value="ready">已有字幕</option>
        </select>
      </div>
    </header>

    <main>
      <div v-if="filteredVideos.length === 0" class="empty">
        <p>还没有视频，点击「添加视频」导入你的第一个学习素材。</p>
      </div>

      <table v-else class="table">
        <thead>
          <tr>
            <th>标题</th>
            <th>时长</th>
            <th>大小</th>
            <th>上传时间</th>
            <th>字幕状态</th>
            <th>标注数</th>
            <th style="width: 260px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in filteredVideos" :key="v.id">
            <td class="title-cell">{{ v.title }}</td>
            <td>{{ formatDuration(v.duration) }}</td>
            <td>{{ formatSize(v.size) }}</td>
            <td>{{ formatDate(v.createdAt) }}</td>
            <td>{{ formatStatus(v.status) }}</td>
            <td>{{ v.notesCount ?? 0 }}</td>
            <td>
              <div class="actions">
                <BaseButton size="sm" @click="goPlayer(v.id)">进入学习</BaseButton>
                <BaseButton size="sm" variant="secondary" @click="onGenerateSubtitles(v)">
                  {{ v.status === 'ready' ? '重新生成字幕' : '生成字幕' }}
                </BaseButton>
                <BaseButton size="sm" variant="ghost" @click="onManageSubtitles(v)">
                  管理字幕
                </BaseButton>
                <BaseButton size="sm" variant="danger" @click="onDelete(v)">删除</BaseButton>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </main>

    <!-- 合规确认对话框（简易实现） -->
    <div v-if="showConsent" class="dialog-backdrop">
      <div class="dialog">
        <h3>导入前提示</h3>
        <p>请确认你对将要导入的视频拥有合法的学习使用权，本应用仅用于个人学习。</p>
        <label class="checkbox">
          <input v-model="consentChecked" type="checkbox" />
          <span>我确认拥有这些视频的学习使用权</span>
        </label>
        <div class="dialog-actions">
          <BaseButton size="sm" variant="ghost" @click="closeConsent">取消</BaseButton>
          <BaseButton size="sm" :disabled="!consentChecked" @click="chooseFiles">
            继续选择文件
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import BaseButton from '../components/BaseButton.vue';
import { useVideosStore } from '../store/videos';
import { useSubtitlesStore } from '../store/subtitles';

const router = useRouter();
const videosStore = useVideosStore();

const keyword = ref('');
const statusFilter = ref<string>('');

const showConsent = ref(false);
const consentChecked = ref(false);

onMounted(() => {
  // 仅为了前端开发演示，后续可去掉
  // @ts-ignore
  if (videosStore.seedMockData) {
    // @ts-ignore
    videosStore.seedMockData();
  }
});

const filteredVideos = computed(() => {
  return videosStore.items.filter((v: any) => {
    const matchKeyword =
      !keyword.value || v.title.toLowerCase().includes(keyword.value.toLowerCase());
    const matchStatus =
      !statusFilter.value || v.status === statusFilter.value;
    return matchKeyword && matchStatus;
  });
});

function onAddVideo() {
  showConsent.value = true;
  consentChecked.value = false;
}

function closeConsent() {
  showConsent.value = false;
  consentChecked.value = false;
}

function chooseFiles() {
  // TODO: 这里后续接 Electron 主进程的文件选择逻辑
  // 现在先关闭弹窗，模拟已选择文件
  showConsent.value = false;
  consentChecked.value = false;
  // 可以在这里调用 videosStore 的导入 action
}

function goPlayer(id: string) {
  router.push({ name: 'player', params: { id } });
}

function onGenerateSubtitles(v: any) {
  // TODO: 调用生成字幕的 action / API
  console.log('generate subtitles for', v.id);
}

function onManageSubtitles(v: any) {
  // TODO: 打开字幕管理弹窗或跳转到字幕页面
  console.log('manage subtitles for', v.id);
}

function onDelete(v: any) {
  if (!confirm(`确定要删除视频「${v.title}」及其本地字幕和笔记吗？`)) return;
  // TODO: 调用删除 action
  console.log('delete video', v.id);
}

function formatDuration(seconds?: number) {
  if (!seconds) return '-';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}分${s.toString().padStart(2, '0')}秒`;
}

function formatSize(bytes?: number) {
  if (!bytes) return '-';
  const mb = bytes / (1024 * 1024);
  if (mb < 1024) return `${mb.toFixed(1)} MB`;
  const gb = mb / 1024;
  return `${gb.toFixed(2)} GB`;
}

function formatDate(iso?: string) {
  if (!iso) return '-';
  try {
    const d = new Date(iso);
    return `${d.getFullYear()}-${(d.getMonth() + 1)
      .toString()
      .padStart(2, '0')}-${d
      .getDate()
      .toString()
      .padStart(2, '0')} ${d.getHours().toString().padStart(2, '0')}:${d
      .getMinutes()
      .toString()
      .padStart(2, '0')}`;
  } catch {
    return iso;
  }
}

function formatStatus(status?: string) {
  switch (status) {
    case 'idle':
      return '未生成字幕';
    case 'processing':
      return '生成中';
    case 'ready':
      return '已有字幕';
    default:
      return '-';
  }
}
</script>

<style scoped>
.videos-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search {
  width: 220px;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  font-size: 13px;
}

.filter {
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  font-size: 13px;
}

.empty {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  color: #6b7280;
  font-size: 14px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
}

.table th,
.table td {
  padding: 8px 10px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 13px;
  text-align: left;
}

.table th {
  background: #f3f4f6;
  font-weight: 500;
}

.title-cell {
  max-width: 260px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 简单对话框样式 */
.dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 40;
}

.dialog {
  width: 380px;
  background: #ffffff;
  border-radius: 10px;
  padding: 16px 18px 14px;
  box-shadow: 0 10px 40px rgba(15, 23, 42, 0.25);
}

.dialog h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.dialog p {
  margin: 0 0 12px;
  font-size: 13px;
  color: #4b5563;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  margin-bottom: 12px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>