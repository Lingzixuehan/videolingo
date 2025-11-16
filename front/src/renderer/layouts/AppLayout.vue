<template>
  <div class="layout">
    <header class="topbar card">
      <div class="left">
        <div class="brand" @click="$router.push('/')">VideoLingo</div>
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
      </div>
      <div class="right" v-if="user.isAuthed">
        <span class="user">{{ user.displayName || user.email }}</span>
        <BaseButton small @click="toggleTheme">{{ themeText }}</BaseButton>
        <BaseButton small variant="danger" @click="doLogout">退出</BaseButton>
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
import { useSettingsStore } from '../store/settings';
import { computed } from 'vue';
import BaseButton from '../components/BaseButton.vue';

const user = useUserStore();
const router = useRouter();
const settings = useSettingsStore();

function doLogout() {
  user.logout();
  router.replace('/login');
}
function toggleTheme() {
  settings.toggleTheme();
}
const themeText = computed(() => settings.theme === 'light' ? '暗色' : '浅色');
</script>

<style scoped>
.layout { min-height:100vh; display:flex; flex-direction:column; }
.topbar {
  display:flex; justify-content:space-between; align-items:center; padding:10px 18px;
  margin:0; border-radius:0; border:0; border-bottom:1px solid var(--c-border); box-shadow:none;
}
.brand { font-weight:700; margin-right:20px; cursor:pointer; }
.nav a {
  margin-right:14px; font-size:14px; color:var(--c-text-dim); padding:6px 8px;
  border-radius:4px; transition:var(--transition);
}
.nav a.router-link-active, .nav a:hover { background:var(--c-primary); color:#fff; }
.right { display:flex; align-items:center; gap:10px; }
.user { font-size:13px; color:var(--c-text-dim); }
.main { flex:1; padding:20px; max-width:1280px; width:100%; margin:0 auto; }
</style>