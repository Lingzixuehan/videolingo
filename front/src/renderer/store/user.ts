import { defineStore } from 'pinia';
import { login as apiLogin, register as apiRegister } from '../api/auth';

interface UserState {
  email: string;
  token: string;
  loading: boolean;
  error: string;
  mode: 'login' | 'register';
}

const STORAGE_KEY = 'user_auth_v1';

function restore(): Partial<UserState> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    email: '',
    token: '',
    loading: false,
    error: '',
    mode: 'login',
    ...restore()
  }),
  getters: {
    isAuthed: (s) => !!s.token
  },
  actions: {
    persist() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ email: this.email, token: this.token })
      );
    },
    setMode(m: 'login' | 'register') {
      this.mode = m;
      this.error = '';
    },
    async login(email: string, password: string) {
      this.loading = true;
      this.error = '';
      try {
        const r = await apiLogin({ email, password });
        this.email = email;
        this.token = r.access_token;
        this.persist();
      } catch (e: any) {
        this.error = e.message || '登录失败';
        throw e;
      } finally {
        this.loading = false;
      }
    },
    async register(email: string, password: string) {
      this.loading = true;
      this.error = '';
      try {
        await apiRegister({ email, password });
        await this.login(email, password); // 注册后自动登录
      } catch (e: any) {
        this.error = e.message || '注册失败';
        throw e;
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.email = '';
      this.token = '';
      this.error = '';
      localStorage.removeItem(STORAGE_KEY);
    }
  }
});