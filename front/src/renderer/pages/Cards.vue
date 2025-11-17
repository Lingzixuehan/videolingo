<template>
  <div class="page cards-page">
    <header class="page-header">
      <h1 class="page-title">学习卡片管理</h1>

      <div class="page-header-actions">
        <input
          v-model="keyword"
          type="text"
          class="input"
          placeholder="按单词或句子搜索卡片"
        />
        <select v-model="filterType" class="input input-select">
          <option value="">全部类型</option>
          <option value="word">单词</option>
          <option value="phrase">短语</option>
          <option value="sentence">句子</option>
          <option value="grammar">语法</option>
          <option value="note">笔记</option>
        </select>
      </div>
    </header>

    <section v-if="filteredCards.length" class="card-list-wrapper">
      <table class="table-reset card-table">
        <thead>
          <tr>
            <th style="width: 80px">类型</th>
            <th>正面</th>
            <th style="width: 130px">掌握度</th>
            <th style="width: 180px">下次复习时间</th>
            <th style="width: 220px">来源视频</th>
            <th style="width: 120px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in filteredCards" :key="c.id">
            <td>
              <span class="tag">{{ formatType(c.type) }}</span>
            </td>
            <td class="card-front">
              {{ c.front }}
            </td>
            <td>
              <span
                class="tag"
                :class="{
                  'tag-hard': c.ease === 'hard',
                  'tag-easy': c.ease === 'easy',
                }"
              >
                {{ formatEase(c.ease) }}
              </span>
            </td>
            <td>
              <div class="text-secondary">
                {{ formatDateTime(c.nextReviewAt) }}
              </div>
            </td>
            <td>
              <div class="text-secondary">
                <div v-if="c.videoTitle">
                  {{ c.videoTitle }}
                </div>
                <div v-if="c.videoTime != null">
                  {{ formatTime(c.videoTime) }}
                </div>
              </div>
            </td>
            <td>
              <button class="btn-link danger" @click="remove(c.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-else class="empty-state">
      <p>还没有任何学习卡片。</p>
      <p class="text-secondary">可以在「视频学习」页面点击字幕中的单词或句子来生成卡片。</p>
    </section>
  </div>
</template>

<script setup lang="ts">
// filepath: d:\savingsomething\CollegeClasses\Soft\MyWork\videolingo\front\src\renderer\pages\Cards.vue
// ...existing code...
import { computed, ref } from 'vue';
import { useCardsStore } from '../store/cards';

const cardsStore = useCardsStore();

const keyword = ref('');
const filterType = ref<string>('');

const allCards = computed(() => cardsStore.itemsAll);

const filteredCards = computed(() => {
  const kw = keyword.value.trim().toLowerCase();
  const type = filterType.value;
  return allCards.value.filter((c) => {
    if (type && c.type !== type) return false;
    if (!kw) return true;
    return (
      c.front.toLowerCase().includes(kw) ||
      (c.back ?? '').toLowerCase().includes(kw)
    );
  });
});

function formatType(t: string | undefined) {
  switch (t) {
    case 'word':
      return '单词';
    case 'phrase':
      return '短语';
    case 'sentence':
      return '句子';
    case 'grammar':
      return '语法';
    case 'note':
      return '笔记';
    default:
      return '未知';
  }
}

function formatEase(ease?: 'hard' | 'normal' | 'easy') {
  switch (ease) {
    case 'hard':
      return '困难';
    case 'easy':
      return '简单';
    default:
      return '一般';
  }
}

function formatDateTime(v?: string) {
  if (!v) return '-';
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return '-';
  return `${d.getFullYear()}-${(d.getMonth() + 1)
    .toString()
    .padStart(2, '0')}-${d
    .getDate()
    .toString()
    .padStart(2, '0')} ${d
    .getHours()
    .toString()
    .padStart(2, '0')}:${d
    .getMinutes()
    .toString()
    .padStart(2, '0')}`;
}

function formatTime(sec: number) {
  if (!Number.isFinite(sec)) return '-';
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m.toString().padStart(2, '0')}:${r.toString().padStart(2, '0')}`;
}

function remove(id: string) {
  if (!confirm('确定要删除这张卡片吗？此操作不可撤销。')) return;
  cardsStore.removeById(id);
}
</script>

<style scoped>
/* 简单复用 theme.css 里的风格 */
.page {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.card-list-wrapper {
  flex: 1;
  overflow: auto;
}

.card-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.card-table th,
.card-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}

.card-front {
  max-width: 420px;
  word-break: break-word;
}

.tag {
  display: inline-flex;
  padding: 2px 8px;
  border-radius: 999px;
  background: #e5e7eb;
  font-size: 12px;
  color: #374151;
}

.tag-hard {
  background: #fee2e2;
  color: #b91c1c;
}

.tag-easy {
  background: #d1fae5;
  color: #047857;
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
}

.btn-link.danger {
  color: #dc2626;
}

.empty-state {
  margin-top: 32px;
  color: #4b5563;
}
</style>