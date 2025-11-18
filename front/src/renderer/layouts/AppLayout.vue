<template>
  <div class="app-frame">
    <div class="app-shell">
      <aside class="sidebar">
        <div class="logo">VideoLingo</div>
        <nav class="nav">
          <RouterLink class="nav-item" :class="{ active: isActive('home') }" :to="{ name: 'home' }">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">概览</span>
          </RouterLink>
          <RouterLink class="nav-item" :class="{ active: isActive('videos') }" :to="{ name: 'videos' }">
            <span class="nav-icon">🎞</span>
            <span class="nav-label">我的视频</span>
          </RouterLink>

          <div class="nav-group-title">学习</div>
          <RouterLink
            class="nav-item sub"
            :class="{ active: isActive('study-review') }"
            :to="{ name: 'study-review' }"
          >
            <span class="nav-icon">📚</span>
            <span class="nav-label">学习复习</span>
          </RouterLink>
          <RouterLink
            class="nav-item sub"
            :class="{ active: isActive('study-cards') }"
            :to="{ name: 'study-cards' }"
          >
            <span class="nav-icon">🗂</span>
            <span class="nav-label">卡片管理</span>
          </RouterLink>

          <div class="nav-group-title">账号与设置</div>
          <RouterLink
            class="nav-item sub"
            :class="{ active: isActive('settings') }"
            :to="{ name: 'settings' }"
          >
            <span class="nav-icon">⚙️</span>
            <span class="nav-label">设置概览</span>
          </RouterLink>
          <RouterLink
            class="nav-item sub"
            :class="{ active: isActive('settings-plan') }"
            :to="{ name: 'settings-plan' }"
          >
            <span class="nav-icon">📅</span>
            <span class="nav-label">学习计划</span>
          </RouterLink>
          <RouterLink
            class="nav-item sub"
            :class="{ active: isActive('settings-privacy') }"
            :to="{ name: 'settings-privacy' }"
          >
            <span class="nav-icon">🔒</span>
            <span class="nav-label">数据与隐私</span>
          </RouterLink>
        </nav>
      </aside>

      <main class="main">
        <header class="topbar">
          <div class="topbar-left">
            <div class="topbar-app">学习工作台</div>
            <h1 class="topbar-title">{{ currentTitle }}</h1>
          </div>
          <div class="topbar-user">
            <span class="username">{{ user.displayName || '未登录' }}</span>
          </div>
        </header>
        <section class="content">
          <RouterView />
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router';
import { useUserStore } from '../store/user';

const route = useRoute();
const user = useUserStore();

const currentTitle = computed(() => {
  return (route.meta.title as string) || 'Videolingo';
});

function isActive(name: string) {
  return route.name === name;
}
</script>

<style scoped>
  .app-frame {
  min-height: 100vh;
  background: radial-gradient(circle at top left, rgba(56, 189, 248, 0.12), transparent 55%),
    radial-gradient(circle at bottom right, rgba(96, 165, 250, 0.12), transparent 60%),
    #020617;
  display: flex;
  align-items: stretch;
  justify-content: center;
  padding: 20px 16px;
  box-sizing: border-box;
}

.app-shell {
  width: 100%;
  max-width: 1440px;
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 14px;
  background:
    radial-gradient(circle at top left, rgba(56, 189, 248, 0.08), transparent 60%),
    radial-gradient(circle at bottom right, rgba(79, 70, 229, 0.18), transparent 65%),
    rgba(15, 23, 42, 0.96);
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.9);
  padding: 14px;
  color: #e5e7eb;
}

.sidebar {
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(30, 64, 175, 0.5);
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.85);
  padding: 14px 12px;
  display: flex;
  flex-direction: column;
}

.logo {
  font-weight: 600;
  font-size: 18px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 16px;
  color: #e5e7eb;
}

.nav {
  flex: 1;
  overflow-y: auto;
}

.nav-group-title {
  font-size: 13px;
  font-weight: 600;
  color: #cbd5f5;
  padding: 16px 10px 6px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 9px 12px;
  margin: 1px 0;
  border-radius: 8px;
  color: #cbd5f5;
  text-decoration: none;
  font-size: 14px;
  transition: background 0.16s ease, color 0.16s ease;
}

.nav-item.sub {
  padding-left: 18px;
}

.nav-item:hover {
  background: rgba(148, 163, 184, 0.16);
  color: #e5e7eb;
}

.nav-item.active {
  background: rgba(30, 64, 175, 0.8);
  border-radius: 8px;
  color: #f9fafb;
}

.nav-icon {
  width: 18px;
  font-size: 14px;
  text-align: center;
}

.nav-label {
  flex: 1;
}

.main {
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.96);
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.7);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  height: 56px;
  padding: 0 18px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.35);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: radial-gradient(circle at top left, rgba(56, 189, 248, 0.05), transparent 60%),
    rgba(15, 23, 42, 0.98);
}

.topbar-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.topbar-app {
  font-size: 13px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #cbd5f5;
  font-weight: 600;
}

.topbar-title {
  font-size: 20px;
  font-weight: 650;
  margin: 0;
}

.topbar-user {
  font-size: 14px;
  color: #e5e7eb;
}

.content {
  flex: 1;
  padding: 14px 18px 18px;
  overflow: auto;
}
</style>