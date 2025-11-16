import { setActivePinia, createPinia } from 'pinia';
import { useSettingsStore } from '../src/renderer/store/settings';

describe('settings store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
  });

  it('default theme', () => {
    const s = useSettingsStore();
    expect(s.theme).toBe('light');
  });

  it('toggle theme', () => {
    const s = useSettingsStore();
    s.toggleTheme();
    expect(['dark','light']).toContain(s.theme);
    expect(document.documentElement.getAttribute('data-theme')).toBe(s.theme);
  });

  it('persist theme', () => {
    const s = useSettingsStore();
    s.setTheme('dark');
    const raw = localStorage.getItem('settings_v1');
    expect(raw).toContain('dark');
  });
});