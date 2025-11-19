import { createPinia } from 'pinia';
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { useSettingsStore } from './store/settings';
import { useVideosStore } from './store/videos';
import './styles/theme.css';

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount('#app');

const settings = useSettingsStore();
settings.init();

// Load existing imported videos (if preload provided API)
(async () => {
	try {
		// @ts-ignore
		if (window.api && typeof window.api.getVideoFiles === 'function') {
			// @ts-ignore
			const files: Array<{ name: string; size: number; url: string }> = await window.api.getVideoFiles();
			if (Array.isArray(files) && files.length > 0) {
				const videosStore = useVideosStore();
				const entries = files.map(f => ({ path: f.name, size: f.size }));
				videosStore.addVideosFromPaths(entries);
			}
		}
	} catch (err) {
		console.warn('init getVideoFiles failed', err);
	}
})();