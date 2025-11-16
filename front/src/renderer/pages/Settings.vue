<template>
  <div class="wrap">
    <h2>设置</h2>
    <div class="card section">
      <h3>主题</h3>
      <p>当前：<strong>{{ settings.theme }}</strong></p>
      <BaseButton variant="primary" @click="settings.toggleTheme()">切换主题</BaseButton>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useSettingsStore } from '../store/settings';
import BaseButton from '../components/BaseButton.vue';
const settings = useSettingsStore();
</script>
<style scoped>
.wrap { padding:4px; }
.section { margin-bottom:20px; }
</style>