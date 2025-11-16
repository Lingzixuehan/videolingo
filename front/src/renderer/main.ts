import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './styles/theme.css';
import { useSettingsStore } from './store/settings';

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount('#app');

const settings = useSettingsStore();
settings.init();