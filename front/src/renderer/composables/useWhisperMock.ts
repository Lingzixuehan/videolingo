import { ref, Ref } from 'vue';
import { useSubtitlesStore } from '../store/subtitles';

export function useWhisperMock(currentVideoId: Ref<string | undefined>, getLocalVideoPath: () => string | null) {
  const subtitlesStore = useSubtitlesStore();
  
  const whisperProcessing = ref(false);
  const extractProgress = ref(0);
  const extractedResult = ref<any>(null);
  const wordLabels = ref<any[]>([]);
  const translationSegments = ref<any[]>([]);
  const extractTaskId = ref<string | null>(null);

  async function startExtract() {
    const path = getLocalVideoPath();
    if (!path) return alert('未找到视频路径');
    whisperProcessing.value = true;
    extractProgress.value = 0;
    try {
      // MOCK FLOW: simulate progress then load example result files from examples/test_output
      extractProgress.value = 0;
      const rndStep = () => Math.max(1, Math.floor(Math.random() * 8));
      while (extractProgress.value < 100) {
        // fast ramp up then slow near the end to feel realistic
        await new Promise((res) => setTimeout(res, 200 + Math.floor(Math.random() * 300)));
        extractProgress.value = Math.min(100, extractProgress.value + rndStep());
      }

      // load example JSON and populate subtitles store
      try {
        const jsonUrl = new URL('../../common/whisper/examples/test_output/input.json', import.meta.url).href;
        const res = await fetch(jsonUrl);
        if (res.ok) {
          const data = await res.json();
          extractedResult.value = data;
          // convert segments -> subtitles
          const segs = data.segments || [];
          const vid = currentVideoId.value ?? 'example';
          const lines = segs.map((s: any, idx: number) => ({
            id: idx + 1,
            videoId: vid,
            start: s.start,
            end: s.end,
            text: s.text.trim(),
            textCn: (s.textCn as string) || undefined,
          }));
          subtitlesStore.setSubtitles(vid, lines);
          alert('（示例模式）提取完成：示例 SRT/JSON 已加载到播放器');
        } else {
          alert('无法加载示例数据: ' + res.status);
        }
      } catch (e) {
        console.error('mock load example json failed', e);
        alert('加载示例数据时出错: ' + e);
      }
    } catch (e) {
      console.error('extract error', e);
      alert('extract 失败: ' + e);
    } finally {
      whisperProcessing.value = false;
      extractTaskId.value = null;
      extractProgress.value = 0;
    }
  }

  async function startTranslateAndEmbed() {
    const path = getLocalVideoPath();
    if (!path) return alert('未找到视频路径');
    whisperProcessing.value = true;
    try {
      // MOCK: simulate translate+embed using example outputs
      extractProgress.value = 0;
      while (extractProgress.value < 100) {
        await new Promise((res) => setTimeout(res, 120 + Math.floor(Math.random() * 240)));
        extractProgress.value = Math.min(100, extractProgress.value + Math.floor(Math.random() * 12) + 4);
      }

      // load example translation file first (sentence-level), fall back to label-based mapping
      try {
        const transUrl = new URL('../../common/whisper/examples/test_output/input-translation.json', import.meta.url).href;
        const trRes = await fetch(transUrl);
        if (trRes.ok) {
          const trj = await trRes.json();
          const mapping = trj.translations || [];
          // ensure segments exist
          if (!extractedResult.value?.segments?.length) {
            try {
              const jsonUrl2 = new URL('../../common/whisper/examples/test_output/input.json', import.meta.url).href;
              const resp2 = await fetch(jsonUrl2);
              if (resp2.ok) extractedResult.value = await resp2.json();
            } catch (ee) {
              console.warn('[Player] fallback load input.json failed', ee);
            }
          }
          const segs = extractedResult.value?.segments || [];
          const vid = currentVideoId.value ?? 'example';

          const lines = segs.map((s: any, idx: number) => {
            const found = mapping.find((m: any) => Math.abs((m.start || 0) - (s.start || 0)) < 0.5) || {};
            return {
              id: idx + 1,
              videoId: vid,
              start: s.start,
              end: s.end,
              text: (s.text || '').trim(),
              textCn: (found.textCn || '').trim() || undefined,
            };
          });

          subtitlesStore.setSubtitles(vid, lines);
          translationSegments.value = lines.map((l: any) => ({ start: l.start, end: l.end, textCn: l.textCn }));
          alert('（示例模式）句子级翻译已加载并嵌入到字幕');
        } else {
          // fallback to previous label-based approach (labels file)
          const srtUrl = new URL('../../common/whisper/examples/test_output/input.srt', import.meta.url).href;
          const srtRes = await fetch(srtUrl);
          if (srtRes.ok) {
            // existing label-based mapping logic remains elsewhere; call startAnalyzeAndLabel to populate labels if needed
            alert('示例翻译文件不存在，已回退到词典式翻译（或请先运行 标注）');
          }
        }
      } catch (e) {
        console.error('mock translate+embed failed', e);
        alert('模拟翻译/嵌入失败: ' + e);
      }
    } catch (e) {
      console.error('translate+embed error', e);
      alert('translate+embed 失败: ' + e);
    } finally {
      whisperProcessing.value = false;
    }
  }

  async function startAnalyzeAndLabel() {
    // If we already have an extracted srt path, use it; otherwise extract first
    const path = getLocalVideoPath();
    if (!path) return alert('未找到视频路径');
    whisperProcessing.value = true;
    try {
      // MOCK: simulate analysis/label using examples/input-labels.json
      extractProgress.value = 0;
      while (extractProgress.value < 100) {
        await new Promise((res) => setTimeout(res, 150 + Math.floor(Math.random() * 200)));
        extractProgress.value = Math.min(100, extractProgress.value + Math.floor(Math.random() * 15) + 3);
      }

      try {
        const labelsUrl = new URL('../../common/whisper/examples/test_output/input-labels.json', import.meta.url).href;
        const r = await fetch(labelsUrl);
        if (r.ok) {
          const json = await r.json();
          // flatten words across blocks
          const blocks = json.blocks || [];
          const words: any[] = [];
          blocks.forEach((b: any) => {
            (b.words || []).forEach((w: any) => words.push(w));
          });
          wordLabels.value = words;
          alert('（示例模式）标注完成：示例 labels 已加载');
          return true; // Signal success to switch tab
        } else {
          alert('无法加载示例 labels: ' + r.status);
        }
      } catch (e) {
        console.error('mock label load failed', e);
        alert('加载示例标注失败: ' + e);
      }
    } catch (e) {
      console.error('label error', e);
      alert('label 失败: ' + e);
    } finally {
      whisperProcessing.value = false;
    }
    return false;
  }

  return {
    whisperProcessing,
    extractProgress,
    extractedResult,
    wordLabels,
    translationSegments,
    startExtract,
    startTranslateAndEmbed,
    startAnalyzeAndLabel
  };
}
