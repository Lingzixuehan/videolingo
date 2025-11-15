export async function readVideoMetadata(file: File): Promise<{ durationSec: number }> {
  const url = URL.createObjectURL(file);
  try {
    const video = document.createElement('video');
    video.preload = 'metadata';
    video.src = url;

    await new Promise<void>((resolve, reject) => {
      const onLoaded = () => resolve();
      const onError = () => reject(new Error('读取视频元数据失败'));
      video.addEventListener('loadedmetadata', onLoaded, { once: true });
      video.addEventListener('error', onError, { once: true });
    });

    const durationSec = Number.isFinite(video.duration) ? video.duration : 0;
    return { durationSec };
  } finally {
    URL.revokeObjectURL(url);
  }
}