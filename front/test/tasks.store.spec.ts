import { setActivePinia, createPinia } from 'pinia';
import { useTasksStore } from '../src/renderer/store/tasks';

describe('tasks store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it('create task', () => {
    const s = useTasksStore();
    const id = s.create('vid1');
    expect(s.items.length).toBe(1);
    expect(s.items[0].id).toBe(id);
    expect(s.items[0].status).toBe('pending');
  });

  it('start -> processing', () => {
    const s = useTasksStore();
    const id = s.create('v');
    s.start(id);
    expect(s.items[0].status).toBe('processing');
  });

  it('progress & finish', () => {
    const s = useTasksStore();
    const id = s.create('v');
    s.start(id);
    s.updateProgress(id, 40);
    expect(s.items[0].progress).toBe(40);
    s.finish(id);
    expect(s.items[0].status).toBe('done');
    expect(s.items[0].progress).toBe(100);
  });

  it('fail & cancel', () => {
    const s = useTasksStore();
    const id = s.create('v');
    s.fail(id, 'error msg'); // pending 直接 fail 也允许
    expect(s.items[0].status).toBe('error');
    s.cancel(id);
    expect(s.items[0].status).toBe('canceled');
  });
});