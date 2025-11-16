<template>
  <div class="wrap">
    <h2>任务列表</h2>
    <div v-if="list.length===0" class="card empty">暂无任务</div>
    <div v-else class="table-wrap card">
      <table class="table-reset">
        <thead>
          <tr>
            <th>类型</th>
            <th>状态</th>
            <th>进度</th>
            <th>视频ID</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in list" :key="t.id">
            <td>{{ t.type }}</td>
            <td><span class="tag" :class="mapStatusClass(t.status)">{{ t.status }}</span></td>
            <td>{{ t.progress }}%</td>
            <td>{{ t.videoId }}</td>
            <td class="ops">
              <BaseButton small v-if="t.status==='pending'" @click="start(t.id)">开始</BaseButton>
              <template v-if="t.status==='processing'">
                <BaseButton small @click="inc(t.id)">+10%</BaseButton>
                <BaseButton small variant="primary" @click="finish(t.id)">完成</BaseButton>
                <BaseButton small variant="danger" @click="fail(t.id)">失败</BaseButton>
              </template>
              <BaseButton small v-if="t.status!=='done' && t.status!=='canceled'" @click="cancel(t.id)">取消</BaseButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { useTasksStore } from '../store/tasks';
import BaseButton from '../components/BaseButton.vue';
const tasks = useTasksStore();
const list = computed(()=> tasks.items);
function start(id:string){ tasks.start(id); }
function inc(id:string){
  const t = tasks.items.find(i=>i.id===id);
  if (!t) return;
  tasks.updateProgress(id, Math.min(100, t.progress + 10));
}
function finish(id:string){ tasks.finish(id); }
function fail(id:string){ tasks.fail(id,'模拟错误'); }
function cancel(id:string){ tasks.cancel(id); }
function mapStatusClass(s:string){
  switch(s){
    case 'processing': return 'primary';
    case 'pending': return 'warn';
    case 'done': return 'success';
    case 'error': return 'danger';
    case 'canceled': return '';
    default: return '';
  }
}
</script>
<style scoped>
.wrap { padding:4px; }
h2 { margin:0 0 16px; }
.empty { padding:24px; text-align:center; }
.table-wrap { overflow-x:auto; }
.ops { display:flex; gap:6px; }
</style>