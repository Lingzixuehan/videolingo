import { setActivePinia, createPinia } from 'pinia';
import { useUserStore } from '../src/renderer/store/user';

vi.mock('../src/renderer/api/auth', () => ({
  login: vi.fn(async ({ email }: { email: string; password: string }) => {
    return { access_token: `TOKEN_${email}`, token_type: 'bearer' };
  }),
  register: vi.fn(async () => {
    return undefined;
  })
}));

describe('user store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it('login persists token/email', async () => {
    const store = useUserStore();
    await store.login('a@b.com', '123');
    expect(store.isAuthed).toBe(true);
    expect(store.token).toBe('TOKEN_a@b.com');
    const raw = localStorage.getItem('user_auth_v1');
    expect(raw).not.toBeNull();
  });

  it('register auto logs in', async () => {
    const store = useUserStore();
    await store.register('x@y.com', 'zzz');
    expect(store.email).toBe('x@y.com');
    expect(store.isAuthed).toBe(true);
  });

  it('logout clears state/localStorage', async () => {
    const store = useUserStore();
    await store.login('t@t.com', 'p');
    store.logout();
    expect(store.isAuthed).toBe(false);
    expect(localStorage.getItem('user_auth_v1')).toBeNull();
  });
});