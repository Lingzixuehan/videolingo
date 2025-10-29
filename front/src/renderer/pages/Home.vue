<template>
  <div class="page">
    <h2>首页</h2>
    <p>欢迎，{{ user.username || '游客' }}</p>
    <nav style="display:flex; gap:12px; margin:12px 0;">
      <router-link to="/player">播放器</router-link>
      <router-link to="/downloads">下载中心</router-link>
      <router-link to="/settings">设置</router-link>
    </nav>
  </div>
</template>
<script setup lang="ts">
import { useUserStore } from '../store/user';
const user = useUserStore();
</script>