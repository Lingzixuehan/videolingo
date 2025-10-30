<template>
  <div class="layout">
    <aside class="sidebar">
      <h3 class="logo">VideoLingo</h3>
      <nav>
        <router-link to="/home">首页</router-link>
        <router-link to="/player">播放器</router-link>
        <router-link to="/downloads">下载中心</router-link>
        <router-link to="/settings">设置</router-link>
      </nav>
    </aside>
    <main class="content">
      <header class="topbar">
        <div class="left">
          <span class="title">{{ title }}</span>
        </div>
        <div class="right">
          <span v-if="user.username">👤 {{ user.username }}</span>
          <button v-if="user.username" @click="logout">退出</button>
        </div>
      </header>
      <section class="page">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../store/user';

const route = useRoute();
const router = useRouter();
const user = useUserStore();

const title = computed(() => {
  const map: Record<string, string> = {
    '/home': '首页',
    '/player': '播放器',
    '/downloads': '下载中心',
    '/settings': '设置'
  };
  return map[route.path] ?? 'VideoLingo';
});

function logout() {
  user.logout();
  router.push('/login');
}
</script>

<style scoped>
.layout { display: grid; grid-template-columns: 220px 1fr; height: 100vh; }
.sidebar { background: #0f172a; color: #e2e8f0; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.logo { margin: 0 0 8px 0; font-size: 18px; }
.sidebar a { display: block; color: #cbd5e1; text-decoration: none; padding: 6px 8px; border-radius: 6px; }
.sidebar a.router-link-active { background: #1e293b; color: #fff; }
.content { display: grid; grid-template-rows: 48px 1fr; }
.topbar { display: flex; align-items: center; justify-content: space-between; padding: 0 12px; border-bottom: 1px solid #e5e7eb; }
.title { font-weight: 600; }
.page { padding: 16px; overflow: auto; }
button { padding: 6px 10px; }
</style>