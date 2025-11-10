import { isAllowedSize, isAllowedDuration, formatBytes, formatDuration, MAX_SIZE_BYTES, MAX_DURATION_SEC } from '../src/renderer/utils/validators';

describe('validators', () => {
  it('size check', () => {
    expect(isAllowedSize(MAX_SIZE_BYTES)).toBe(true);
    expect(isAllowedSize(MAX_SIZE_BYTES + 1)).toBe(false);
  });
  it('duration check', () => {
    expect(isAllowedDuration(MAX_DURATION_SEC)).toBe(true);
    expect(isAllowedDuration(MAX_DURATION_SEC + 1)).toBe(false);
  });
  it('format helpers', () => {
    expect(formatBytes(1024)).toContain('KB');
    expect(formatDuration(125)).toBe('2:05');
  });
});