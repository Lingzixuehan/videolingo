export const MAX_SIZE_BYTES = 500 * 1024 * 1024; // 500MB
export const MAX_DURATION_SEC = 20 * 60; // 20 分钟

export function isAllowedSize(bytes: number): boolean {
  return bytes <= MAX_SIZE_BYTES;
}

export function isAllowedDuration(seconds: number): boolean {
  return seconds <= MAX_DURATION_SEC;
}

export function formatBytes(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let n = bytes;
  while (n >= 1024 && i < units.length - 1) {
    n /= 1024;
    i++;
  }
  return `${n.toFixed(2)} ${units[i]}`;
}

export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}