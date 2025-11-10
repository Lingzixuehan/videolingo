import { api, API_BASE } from '../src/renderer/api/http';

describe('http client', () => {
  beforeEach(() => {
    // mock fetch
    // @ts-ignore
    global.fetch = vi.fn(async (url: string, opts: any) => {
      if (url.endsWith('/ok')) {
        return {
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify({ success: true, auth: opts?.headers?.Authorization || null })
        };
      }
      return {
        ok: false,
        status: 404,
        text: async () => 'Not Found'
      };
    });
    localStorage.clear();
  });

  it('API_BASE has default or env value', () => {
    expect(API_BASE).toBeTruthy();
  });

  it('get success without token', async () => {
    const data = await api.get<{ success: boolean; auth: string | null }>('/ok');
    expect(data.success).toBe(true);
    expect(data.auth).toBeNull();
  });

  it('get success with token attaches Authorization', async () => {
    localStorage.setItem('token', 'T123');
    const data = await api.get<{ success: boolean; auth: string | null }>('/ok');
    expect(data.auth).toMatch(/Bearer T123/);
  });

  it('error path throws Error', async () => {
    await expect(api.get('/missing')).rejects.toThrow('Not Found');
  });
});