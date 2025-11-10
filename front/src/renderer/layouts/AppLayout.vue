<template>
  <div class="layout">
    <header class="topbar">
      <nav class="nav">
        <router-link to="/">首页</router-link>
        <router-link to="/videos">视频</router-link>
        <router-link to="/tasks">任务</router-link>
        <router-link to="/subtitles">字幕</router-link>
        <router-link to="/player">播放器</router-link>
        <router-link to="/review">复习</router-link>
        <router-link to="/analyze">分析</router-link>
        <router-link to="/settings">设置</router-link>
      </nav>
      <div v-if="user.isAuthed" class="user-box">
        <span class="email">{{ user.displayName || user.email }}</span>
        <button @click="doLogout">退出</button>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '../store/user';
import { useRouter } from 'vue-router';
const user = useUserStore();
const router = useRouter();
function doLogout() {
  user.logout();
  router.replace('/login');
}
</script>

<style scoped>
.layout { display:flex; flex-direction:column; min-height:100vh; }
.topbar {
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:8px 16px;
  background:#1f2937;
  color:#fff;
}
.nav a { margin-right:12px; color:#fff; text-decoration:none; }
.nav a.router-link-active { font-weight:600; text-decoration:underline; }
.user-box { display:flex; align-items:center; gap:8px; }
.email { font-size:13px; opacity:.85; }
button { cursor:pointer; padding:4px 10px; }
.main { flex:1; padding:16px; background:#f5f6f8; }
</style>