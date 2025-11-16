<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="logo">Videolingo</div>
      <nav class="nav">
        <RouterLink class="nav-item" :class="{ active: isActive('home') }" :to="{ name: 'home' }">
          概览
        </RouterLink>
        <RouterLink class="nav-item" :class="{ active: isActive('videos') }" :to="{ name: 'videos' }">
          我的视频
        </RouterLink>

        <div class="nav-group-title">学习</div>
        <RouterLink
          class="nav-item sub"
          :class="{ active: isActive('study-review') }"
          :to="{ name: 'study-review' }"
        >
          学习复习
        </RouterLink>
        <RouterLink
          class="nav-item sub"
          :class="{ active: isActive('study-cards') }"
          :to="{ name: 'study-cards' }"
        >
          卡片管理
        </RouterLink>

        <div class="nav-group-title">账号与设置</div>
        <RouterLink
          class="nav-item sub"
          :class="{ active: isSettingsActive }"
          :to="{ name: 'settings' }"
        >
          设置概览
        </RouterLink>
        <RouterLink
          class="nav-item sub"
          :class="{ active: isActive('settings-plan') }"
          :to="{ name: 'settings-plan' }"
        >
          学习计划
        </RouterLink>
        <RouterLink
          class="nav-item sub"
          :class="{ active: isActive('settings-privacy') }"
          :to="{ name: 'settings-privacy' }"
        >
          数据与隐私
        </RouterLink>
      </nav>
    </aside>

    <main class="main">
      <header class="topbar">
        <h1 class="topbar-title">{{ currentTitle }}</h1>
        <div class="topbar-user">
          <span class="username">{{ user.displayName || '未登录' }}</span>
        </div>
      </header>
      <section class="content">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, RouterLink, RouterView } from 'vue-router';
import { useUserStore } from '../store/user';

const route = useRoute();
const user = useUserStore();

const currentTitle = computed(() => {
  return (route.meta.title as string) || 'Videolingo';
});

function isActive(name: string) {
  return route.name === name;
}

const isSettingsActive = computed(() =>
  ['settings', 'settings-profile', 'settings-plan', 'settings-privacy'].includes(
    (route.name as string) || '',
  ),
);
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
  color: #111827;
}

.sidebar {
  width: 220px;
  background: #111827;
  color: #e5e7eb;
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
}

.logo {
  font-weight: 600;
  font-size: 18px;
  margin-bottom: 16px;
}

.nav {
  flex: 1;
  overflow-y: auto;
}

.nav-group-title {
  font-size: 12px;
  text-transform: uppercase;
  color: #9ca3af;
  padding: 10px 8px 4px;
}

.nav-item {
  display: block;
  padding: 8px 10px;
  margin: 2px 0;
  border-radius: 6px;
  color: #e5e7eb;
  text-decoration: none;
  font-size: 14px;
}

.nav-item.sub {
  padding-left: 20px;
}

.nav-item:hover {
  background: #1f2937;
}

.nav-item.active {
  background: #2563eb;
  color: #ffffff;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  height: 52px;
  padding: 0 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
}

.topbar-title {
  font-size: 18px;
  font-weight: 500;
  margin: 0;
}

.topbar-user {
  font-size: 14px;
  color: #4b5563;
}

.content {
  flex: 1;
  padding: 16px 20px 20px;
  overflow: auto;
}
</style>