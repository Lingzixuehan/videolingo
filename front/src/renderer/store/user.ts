import { defineStore } from 'pinia';
import { login as apiLogin, register as apiRegister } from '../api/auth';

interface UserState {
  email: string;
  username: string;
  token: string;
  loading: boolean;
  error: string;
  mode: 'login' | 'register';
}

const STORAGE_KEY = 'user_auth_v1';

const DEV_ENABLED = import.meta.env.DEV || import.meta.env.VITE_DEV_LOGIN === '1';

const FORCE_REQUIRE_LOGIN = import.meta.env.VITE_REQUIRE_LOGIN === '1';

function restore(): Partial<UserState> {
  if (FORCE_REQUIRE_LOGIN) return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    email: '',
    username: '',
    token: '',
    loading: false,
    error: '',
    mode: 'login',
    ...restore()
  }),
  getters: {
    isAuthed: s => !!s.token,
    displayName: s => s.username || s.email
  },
  actions: {
    persist() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ email: this.email, username: this.username, token: this.token })
      );
    },
    setMode(m: 'login' | 'register') {
      this.mode = m;
      this.error = '';
    },
    async login(email: string, password: string, identifier?: string) {
      this.loading = true;
      this.error = '';
      try {
        if (
          DEV_ENABLED &&
          password === 'test' &&
          (
            (identifier && identifier === 'test') ||
            email === 'test' ||
            email.startsWith('test@')
          )
        ) {
          this.email = email.includes('@') ? email : 'test@local.dev';
          this.username = (identifier && !identifier.includes('@')) ? identifier : 'test';
          this.token = 'DEV_TOKEN';
          this.persist();
          return;
        }


        const r = await apiLogin({ email, password });
        this.email = email;
        this.username = (identifier && !identifier.includes('@')) ? identifier : '';
        this.token = r.access_token;
        this.persist();
      } catch (e: any) {
        this.error = e.message || '登录失败';
        throw e;
      } finally {
        this.loading = false;
      }
    },
    async register(email: string, password: string, identifier?: string) {
      this.loading = true;
      this.error = '';
      try {
        await apiRegister({ email, password });
        await this.login(email, password, identifier);
      } catch (e: any) {
        this.error = e.message || '注册失败';
        throw e;
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.email = '';
      this.username = '';
      this.token = '';
      this.error = '';
      localStorage.removeItem(STORAGE_KEY);
    }
  }
});