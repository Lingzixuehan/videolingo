<template>
  <div class="wrap">
    <h2>任务列表</h2>
    <p v-if="list.length===0">暂无任务</p>
    <ul v-else class="list">
      <li v-for="t in list" :key="t.id" class="item">
        <div class="info">
          <div class="line">
            <strong>{{ t.type }}</strong>
            <span class="status" :class="t.status">{{ t.status }}</span>
          </div>
          <div class="meta">
            <span>视频: {{ t.videoId }}</span>
            <span v-if="t.status==='processing'">进度: {{ t.progress }}%</span>
            <span v-if="t.error" class="err">错误: {{ t.error }}</span>
          </div>
        </div>
        <div class="ops">
          <button v-if="t.status==='pending'" @click="start(t.id)">开始</button>
            <template v-if="t.status==='processing'">
              <button @click="inc(t.id)">+10%</button>
              <button @click="finish(t.id)">完成</button>
              <button @click="fail(t.id)">失败</button>
            </template>
          <button v-if="t.status!=='done' && t.status!=='canceled'" @click="cancel(t.id)">取消</button>
        </div>
      </li>
    </ul>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { useTasksStore } from '../store/tasks';
const tasks = useTasksStore();
const list = computed(()=>tasks.items);
function start(id:string){ tasks.start(id); }
function inc(id:string){
  const t = tasks.items.find(i=>i.id===id);
  if(!t) return;
  tasks.updateProgress(id, Math.min(100, t.progress + 10));
}
function finish(id:string){ tasks.finish(id); }
function fail(id:string){ tasks.fail(id,'模拟错误'); }
function cancel(id:string){ tasks.cancel(id); }
</script>
<style scoped>
.wrap { padding:16px; }
.list { list-style:none; padding:0; margin:12px 0; display:flex; flex-direction:column; gap:10px; }
.item { background:#fff; border:1px solid #e5e7eb; border-radius:6px; padding:12px; display:flex; justify-content:space-between; gap:16px; }
.info { flex:1; }
.line { display:flex; gap:8px; align-items:center; }
.status { font-size:12px; padding:2px 6px; border-radius:4px; background:#eef; text-transform:uppercase; }
.status.processing { background:#dbeafe; }
.status.pending { background:#fef3c7; }
.status.done { background:#dcfce7; }
.status.error { background:#fee2e2; }
.status.canceled { background:#e5e7eb; }
.meta { display:flex; gap:10px; font-size:12px; color:#555; flex-wrap:wrap; margin-top:4px; }
.err { color:#c00; }
.ops button { margin-left:6px; }
</style>