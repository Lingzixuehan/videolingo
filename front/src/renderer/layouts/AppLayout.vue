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

function doLogout() {
  user.logout();
  router.replace('/login');
}

</script>

<template>
  <header class="topbar">
    <nav class="nav">
      <router-link to="/">首页</router-link>
      <router-link to="/downloads">视频</router-link>
      <router-link to="/player">播放器</router-link>
      <router-link to="/settings">设置</router-link>
    </nav>
    <div v-if="user.isAuthed" class="user-box">
      <span class="email">{{ user.email }}</span>
      <button @click="doLogout">退出</button>
    </div>
  </header>
  <main>
    <router-view />
  </main>
</template>

<style scoped>
.topbar {
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:8px 16px;
  background:#1f2937;
  color:#fff;
}
.nav a {
  margin-right:12px;
  color:#fff;
  text-decoration:none;
}
.nav a.router-link-active {
  font-weight:600;
  text-decoration:underline;
}
.user-box {
  display:flex;
  align-items:center;
  gap:8px;
}
.email {
  font-size:13px;
  opacity:.85;
}
button {
  cursor:pointer;
  padding:4px 10px;
}
</style>