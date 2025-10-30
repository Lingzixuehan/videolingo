import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({ username: '' as string, token: '' as string }),
  actions: {
    async login(username: string, _password: string) {
      this.username = username;
      this.token = 'dev-token';
    },
    logout() {
      this.username = ''; this.token = '';
    }
  }
});