import { defineStore } from 'pinia';

interface SettingsState { theme: 'light' | 'dark'; }
const KEY = 'settings_v1';

function restore(): Partial<SettingsState> {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : {};
  } catch { return {}; }
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({
    theme: 'light',
    ...restore()
  }),
  actions: {
    setTheme(t:'light'|'dark') {
      this.theme = t;
      localStorage.setItem(KEY, JSON.stringify({ theme: t }));
      document.documentElement.setAttribute('data-theme', t);
    },
    init() {
      document.documentElement.setAttribute('data-theme', this.theme);
    },
    toggleTheme() {
      this.setTheme(this.theme === 'light' ? 'dark' : 'light');
    }
  }
});