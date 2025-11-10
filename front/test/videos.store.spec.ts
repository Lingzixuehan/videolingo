import { setActivePinia, createPinia } from 'pinia';
import { useVideosStore } from '../src/renderer/store/videos';
import { MAX_DURATION_SEC } from '../src/renderer/utils/validators';

describe('videos store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it('addFromFile accepts valid file and persists', () => {
    const store = useVideosStore();
    const file = new File(['x'.repeat(1024)], 'demo.mp4', { type: 'video/mp4' }); // 1KB
    store.addFromFile(file, 10);
    expect(store.items.length).toBe(1);
    const raw = localStorage.getItem('videos_v1');
    expect(raw).toBeTruthy();
  });

  it('rejects too large size', () => {
    const store = useVideosStore();
    const fakeBig = { name: 'big.mp4', size: 600 * 1024 * 1024 } as File; // 仅模拟
    store.addFromFile(fakeBig, 10);
    expect(store.items.length).toBe(0);
    expect(store.error).toMatch(/文件过大/);
  });

  it('rejects too long duration', () => {
    const store = useVideosStore();
    const file = new File(['x'.repeat(1024)], 'long.mp4', { type: 'video/mp4' });
    store.addFromFile(file, MAX_DURATION_SEC + 1);
    expect(store.items.length).toBe(0);
    expect(store.error).toMatch(/视频过长/);
  });

  it('remove works', () => {
    const store = useVideosStore();
    const file = new File(['x'], 'a.mp4', { type: 'video/mp4' });
    store.addFromFile(file, 5);
    const id = store.items[0].id;
    store.remove(id);
    expect(store.items.length).toBe(0);
  });
});