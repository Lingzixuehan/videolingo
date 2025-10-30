<template>
  <div class="page">
    <h2>登录</h2>
    <form @submit.prevent="submit">
      <input v-model="username" placeholder="用户名" />
      <input v-model="password" type="password" placeholder="密码" />
      <button>登录</button>
    </form>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { useRouter } from 'vue-router';
const username = ref(''); const password = ref('');
const router = useRouter(); const user = useUserStore();
async function submit() {
  await user.login(username.value, password.value);
  router.push('/home');
}
</script>