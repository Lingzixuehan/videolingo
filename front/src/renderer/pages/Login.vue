<template>
  <div class="auth-wrapper">
    <h2>{{ title }}</h2>
    <form class="auth-form" @submit.prevent="submit">
      <label class="field">
        <span>邮箱</span>
        <input v-model="email" type="email" required autocomplete="email" />
      </label>
      <label class="field">
        <span>密码</span>
        <input v-model="password" type="password" required autocomplete="current-password" />
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

const email = ref(user.email || '');
const password = ref('');

const loading = computed(() => user.loading);
const error = computed(() => user.error);
const title = computed(() => user.mode === 'login' ? '登录' : '注册');
const buttonText = computed(() => user.mode === 'login' ? '登录' : '注册并登录');

async function submit() {
  if (!email.value || !password.value) return;
  try {
    if (user.mode === 'login') {
      await user.login(email.value, password.value);
    } else {
      await user.register(email.value, password.value);
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