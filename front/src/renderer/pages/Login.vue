<template>
  <div class="auth-wrapper">
    <h2>{{ title }}</h2>
    <form class="auth-form" @submit.prevent="submit">
      <label class="field">
        <span>用户名或邮箱</span>
        <input v-model.trim="identifier" type="text" required autocomplete="username email" />
      </label>
      <label class="field">
        <span>密码</span>
        <input v-model.trim="password" type="password" required autocomplete="current-password" />
      </label>
      <button type="submit" :disabled="loading">
        {{ loading ? '处理中...' : buttonText }}
      </button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <div class="switch">
      <button v-if="user.mode==='login'" @click="user.setMode('register')">没有账号？注册</button>
      <button v-else @click="user.setMode('login')">已有账号？去登录</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '../store/user';
import { useRouter } from 'vue-router';
import { computed, ref, watch } from 'vue';

const user = useUserStore();
const router = useRouter();

const identifier = ref(user.username || user.email || '');
const password = ref('');

const loading = computed(() => user.loading);
const error = computed(() => user.error);
const title = computed(() => user.mode === 'login' ? '登录' : '注册');
const buttonText = computed(() => user.mode === 'login' ? '登录' : '注册并登录');

function normalizeToEmail(id: string) {
  return id.includes('@') ? id : `${id}@placeholder.local`;
}

async function submit() {
  if (!identifier.value || !password.value) return;
  const email = normalizeToEmail(identifier.value);
  try {
    if (user.mode === 'login') {
      await user.login(email, password.value, identifier.value);
    } else {
      await user.register(email, password.value, identifier.value);
    }
    router.replace('/');
  } catch {
    // error handled in store
  }
}

watch(() => user.mode, () => {
  password.value = '';
});
</script>

<style scoped>
.auth-wrapper {
  max-width: 360px;
  margin: 48px auto;
  padding: 24px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.field span {
  display: block;
  font-size: 12px;
  margin-bottom: 4px;
  color: #555;
}
input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  padding: 10px 14px;
  cursor: pointer;
}
.error {
  color: #c00;
  margin-top: 12px;
  font-size: 14px;
}
.switch {
  margin-top: 18px;
  text-align: center;
}
</style>