export async function health() {
  const res = await fetch('http://127.0.0.1:8000/health');
  return res.json();
}

export async function extract(videoPath: string) {
  const res = await fetch('http://127.0.0.1:8000/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ video_path: videoPath }),
  });
  return res.json();
}

export async function extractWithTask(videoPath: string) {
  const res = await fetch('http://127.0.0.1:8000/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ video_path: videoPath }),
  });
  return res.json(); // { ok: true, task_id }
}

export async function getTaskStatus(taskId: string) {
  const res = await fetch(`http://127.0.0.1:8000/status/${taskId}`);
  return res.json();
}

export async function getTaskResult(taskId: string) {
  const res = await fetch(`http://127.0.0.1:8000/result/${taskId}`);
  return res.json();
}

export async function label(srtPath: string) {
  const res = await fetch('http://127.0.0.1:8000/label', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ srt_path: srtPath }),
  });
  return res.json();
}

export async function embed(videoPath: string, srtPath: string) {
  const res = await fetch('http://127.0.0.1:8000/embed', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ video_path: videoPath, srt_path: srtPath }),
  });
  return res.json();
}

export async function translate(srtPath: string, fromLang = 'en', toLang = 'zh-CHS') {
  const res = await fetch('http://127.0.0.1:8000/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ srt_path: srtPath, from_lang: fromLang, to_lang: toLang }),
  });
  return res.json();
}
