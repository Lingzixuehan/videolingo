<template>
  <div class="page videos-page">
    <header class="page-header">
      <h1 class="page-title">我的视频</h1>

      <div class="page-header-actions">
        <input
          v-model="keyword"
          type="text"
          class="input"
          placeholder="按标题搜索视频"
        />
        <select v-model="statusFilter" class="input input-select">
          <option value="">全部状态</option>
          <option value="no-sub">暂无字幕</option>
          <option value="has-sub">已有字幕</option>
        </select>

        <BaseButton size="sm" @click="onClickAddVideo">添加视频</BaseButton>
      </div>
    </header>

    <!-- 合规弹窗 -->
    <div v-if="showConsent" class="consent-backdrop" @click.self="closeConsent">
      <div class="consent-dialog">
        <h2 class="consent-title">使用前确认</h2>
        <p class="consent-text">
          本应用仅用于个人学习，请确保你对所导入的视频拥有合法的学习使用权，不得用于传播、商业用途或其他违法违规行为。
        </p>
        <label class="consent-checkbox">
          <input v-model="consentChecked" type="checkbox" />
          <span>我已阅读并同意以上说明</span>
        </label>
        <div class="consent-actions">
          <button class="btn-secondary" @click="closeConsent">取消</button>
          <button class="btn-primary" :disabled="!consentChecked" @click="confirmConsent">
            继续选择视频
          </button>
        </div>
      </div>
    </div>

    <section v-if="filteredVideos.length" class="video-list-wrapper">
      <table class="table-reset video-table">
        <thead>
          <tr>
            <th>标题</th>
            <th style="width: 120px">时长</th>
            <th style="width: 120px">大小</th>
            <th style="width: 120px">字幕状态</th>
            <th style="width: 220px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in filteredVideos" :key="v.id">
            <td class="video-title-cell">
              <div class="video-title">{{ v.title }}</div>
              <div class="video-path" v-if="v.filePath">{{ v.filePath }}</div>
            </td>
            <td>{{ formatDuration(v.duration) }}</td>
            <td>{{ formatSize(v.size) }}</td>
            <td>
              <span class="tag" :class="subtitleStatusClass(v)">
                {{ subtitleStatusText(v) }}
              </span>
            </td>
            <td>
              <button class="btn-link" @click="goPlayer(v.id)">进入学习</button>
              <button class="btn-link" @click="onGenerateSubtitles(v)">生成字幕</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-else class="empty-state">
      <p>还没有导入任何视频。</p>
      <p class="text-secondary">点击右上角「添加视频」开始你的第一个学习视频。</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import BaseButton from '../components/BaseButton.vue';
import { useVideosStore } from '../store/videos';

const router = useRouter();
const videosStore = useVideosStore();

declare global {
  interface Window {
    api?: {
      pickVideo: () => Promise<{ canceled: boolean; filePaths: string[] }>;
      getFileInfo?: (path: string) => Promise<{ size: number }>;
    };
  }
}

const keyword = ref('');
const statusFilter = ref<string>('');

const showConsent = ref(false);
const consentChecked = ref(false);

onMounted(() => {
  // 保证刷新后至少有一个示例视频
  videosStore.ensureBuiltinSample();
});

const videos = computed(() => videosStore.items);

const filteredVideos = computed(() => {
  const kw = keyword.value.trim().toLowerCase();
  const status = statusFilter.value;
  return videos.value.filter((v) => {
    if (kw && !v.title.toLowerCase().includes(kw)) return false;
    if (status === 'no-sub' && (v as any).status === 'ready') return false;
    if (status === 'has-sub' && (v as any).status !== 'ready') return false;
    return true;
  });
});

function formatDuration(sec?: number) {
  if (!sec || !Number.isFinite(sec)) return '--:--';
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m.toString().padStart(2, '0')}:${r.toString().padStart(2, '0')}`;
}

function formatSize(bytes?: number) {
  if (!bytes || !Number.isFinite(bytes)) return '-';
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(0)} KB`;
  const mb = kb / 1024;
  if (mb < 1024) return `${mb.toFixed(1)} MB`;
  const gb = mb / 1024;
  return `${gb.toFixed(2)} GB`;
}

function subtitleStatusText(v: { status?: string }) {
  return v.status === 'ready' ? '已有字幕' : '暂无字幕';
}

function subtitleStatusClass(v: { status?: string }) {
  return v.status === 'ready' ? 'tag-success' : 'tag-gray';
}

function goPlayer(id: string) {
  router.push({ name: 'player', params: { id } });
}

function onClickAddVideo() {
  showConsent.value = true;
  consentChecked.value = false;
}

function closeConsent() {
  showConsent.value = false;
}

async function confirmConsent() {
  if (!consentChecked.value) return;
  showConsent.value = false;
  await pickAndAddVideos();
}

async function pickAndAddVideos() {
  const api = window.api;
  if (!api || !api.pickVideo) {
    alert('当前环境不支持选择本地视频（缺少 Electron API）。');
    return;
  }

  try {
    const result = await api.pickVideo();
    if (result.canceled || !result.filePaths.length) return;

    const fileInfos: { path: string; size?: number }[] = [];
    for (const path of result.filePaths) {
      let size: number | undefined;
      if (api.getFileInfo) {
        try {
          const info = await api.getFileInfo(path);
          size = info.size;
        } catch (e) {
          console.warn('获取文件大小失败', path, e);
        }
      }
      fileInfos.push({ path, size });
    }

    videosStore.addVideosFromPaths(fileInfos);
  } catch (err) {
    console.error('pickVideo error:', err);
    alert('选择视频时出现错误，请稍后重试。');
  }
}

function onGenerateSubtitles(_v: any) {
  alert('字幕生成功能稍后接入：会调用后端/本地 Whisper 生成字幕。');
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.page-header-actions {
  display: flex;
  gap: 8px;
}

.input {
  height: 32px;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  font-size: 13px;
}

.input-select {
  min-width: 120px;
}

.video-list-wrapper {
  flex: 1;
  overflow: auto;
}

.video-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.video-table th,
.video-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}

.video-title-cell {
  max-width: 420px;
}

.video-title {
  font-weight: 500;
}

.video-path {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 2px;
}

.tag {
  display: inline-flex;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
}

.tag-success {
  background: #dcfce7;
  color: #15803d;
}

.tag-gray {
  background: #e5e7eb;
  color: #374151;
}

.text-secondary {
  color: #6b7280;
  font-size: 12px;
}

.btn-link {
  background: transparent;
  border: none;
  padding: 0;
  font-size: 13px;
  cursor: pointer;
  color: #2563eb;
  margin-right: 8px;
}

.empty-state {
  margin-top: 40px;
  color: #4b5563;
}

/* 合规弹窗样式 */
.consent-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 40;
}

.consent-dialog {
  width: 420px;
  max-width: 90vw;
  background: #ffffff;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.45);
}

.consent-title {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
}

.consent-text {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 12px;
}

.consent-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #374151;
  margin-bottom: 16px;
}

.consent-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-primary,
.btn-secondary {
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 13px;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: #2563eb;
  color: #ffffff;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: default;
}

.btn-secondary {
  background: #e5e7eb;
  color: #111827;
}
</style>