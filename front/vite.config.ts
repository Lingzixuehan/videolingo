import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, 'src/renderer'),
  plugins: [vue()],
  server: {
    port: 5173,
    strictPort: true
  },
  build: {
    outDir: path.resolve(__dirname, 'dist/renderer'),
    emptyOutDir: true
  }
});



//测试时用以下部分，  npm run test

// import { defineConfig } from 'vitest/config';

// export default defineConfig({
//   test: {
//     environment: 'jsdom',
//     globals: true,
//     include: ['test/**/*.spec.ts']
//   }
// });