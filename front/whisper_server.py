#!/usr/bin/env python3
"""
Lightweight FastAPI wrapper to expose the local `whisper` module as HTTP endpoints.
This is a temporary, desktop-only helper so the Electron front-end can call subtitle
extraction / translation / embedding / labeling without moving the code into the
backend. See `front/src/common/whisper/README.md` for notes.

Run (from `front`):
  python whisper_server.py

Endpoints:
  GET  /health
  POST /extract    { "video_path": "/abs/path/or/relative/file.mp4" }
  POST /label      { "srt_path": "/path/to/file.srt" }
  POST /embed      { "video_path": "...", "srt_path": "..." }
  POST /translate  { "srt_path": "...", "from_lang": "en", "to_lang": "zh-CHS" }

Note: imports from the `whisper` package are done lazily so the server can start
even if heavy dependencies are missing; the actual endpoints will raise clear
errors if dependencies aren't installed.
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import threading
import time

BASE = os.path.dirname(__file__)
# Add path so we can import the whisper package at `front/src/common/whisper`.
sys.path.insert(0, os.path.join(BASE, 'src', 'common'))

app = FastAPI(title='Videolingo Whisper Local Service (temporary)')

# Allow requests from the Electron renderer / dev server
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory task store for background jobs (task_id -> info)
_TASKS = {}
_TASKS_LOCK = threading.Lock()


class ExtractReq(BaseModel):
    video_path: str


class LabelReq(BaseModel):
    srt_path: str


class EmbedReq(BaseModel):
    video_path: str
    srt_path: str


class TranslateReq(BaseModel):
    srt_path: str
    from_lang: str = 'en'
    to_lang: str = 'zh-CHS'


@app.get('/health')
def health():
    return {'ok': True}


@app.post('/extract')
def extract(req: ExtractReq):
    try:
        from whisper.core.subtitle_extractor import SubtitleExtractor
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Import whisper failed: {e}')

    task_id = str(uuid.uuid4())
    # initialize task
    with _TASKS_LOCK:
        _TASKS[task_id] = {'status': 'pending', 'progress': 0, 'message': '', 'result': None}

    def run_extract(tid: str, video_path: str):
        try:
            with _TASKS_LOCK:
                _TASKS[tid]['status'] = 'running'
                _TASKS[tid]['progress'] = 0
            extractor = SubtitleExtractor(model='base')

            import re

            def progress_cb(msg):
                """The SubtitleExtractor passes textual lines to the callback.
                Parse percent information if present, otherwise use heuristics.
                """
                try:
                    text = str(msg)
                except Exception:
                    text = ''
                p = None
                # Try to find a pattern like '12%' or '12.3%'
                m = re.search(r"(\d{1,3})(?:\.\d+)?%", text)
                if m:
                    try:
                        p = int(m.group(1))
                    except Exception:
                        p = None

                # Some whisper lines include 'Done' or '完成' -> set 100
                if p is None:
                    if '完成' in text or 'Done' in text or '字幕提取完成' in text:
                        p = 100
                    elif '开始' in text or 'Starting' in text:
                        p = 1
                    else:
                        # no percent info; keep previous progress or set small increment
                        with _TASKS_LOCK:
                            prev = _TASKS[tid].get('progress', 0)
                        # don't decrease
                        p = prev

                with _TASKS_LOCK:
                    # clamp
                    p = max(0, min(100, int(p))) if p is not None else _TASKS[tid].get('progress', 0)
                    _TASKS[tid]['progress'] = p
                    _TASKS[tid]['message'] = text

            outdir = os.path.join(BASE, 'whisper_output')
            os.makedirs(outdir, exist_ok=True)

            # call extractor with progress callback if supported
            res = extractor.extract(video_path=video_path, output_dir=outdir, progress_callback=progress_cb)

            with _TASKS_LOCK:
                _TASKS[tid]['status'] = 'done'
                _TASKS[tid]['progress'] = 100
                _TASKS[tid]['result'] = res
        except Exception as e:
            with _TASKS_LOCK:
                _TASKS[tid]['status'] = 'error'
                _TASKS[tid]['message'] = str(e)

    thread = threading.Thread(target=run_extract, args=(task_id, req.video_path), daemon=True)
    thread.start()

    return {'ok': True, 'task_id': task_id}


@app.post('/label')
def label(req: LabelReq):
    try:
        from whisper.core.label import Labeler
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Import whisper label failed: {e}')

    try:
        labeler = Labeler()
        res = labeler.process_subtitle_file(req.srt_path)
        return {'ok': True, 'result': res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/status/{task_id}')
def get_status(task_id: str):
    with _TASKS_LOCK:
        info = _TASKS.get(task_id)
    if not info:
        raise HTTPException(status_code=404, detail='task not found')
    return {'ok': True, 'task_id': task_id, 'status': info['status'], 'progress': info.get('progress', 0), 'message': info.get('message', ''), 'result_available': info.get('result') is not None}


@app.get('/result/{task_id}')
def get_result(task_id: str):
    with _TASKS_LOCK:
        info = _TASKS.get(task_id)
    if not info:
        raise HTTPException(status_code=404, detail='task not found')
    if info['status'] != 'done':
        raise HTTPException(status_code=400, detail='result not ready')
    return {'ok': True, 'result': info.get('result')}


@app.post('/embed')
def embed(req: EmbedReq):
    try:
        from whisper.core.subtitle_embedder import SubtitleEmbedder
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Import whisper embedder failed: {e}')

    try:
        embedder = SubtitleEmbedder()
        out = embedder.embed(video_path=req.video_path, subtitle_path=req.srt_path)
        return {'ok': True, 'output': out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/translate')
def translate(req: TranslateReq):
    try:
        from whisper.core.translator import youdao_translate, collect_subtitle_blocks, split_translation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Import whisper translator failed: {e}')

    try:
        blocks, text_blocks = collect_subtitle_blocks(req.srt_path)
        full_text = ' '.join(t for t, _ in text_blocks)
        zh = youdao_translate(full_text, from_lang=req.from_lang, to_lang=req.to_lang)
        segments = split_translation(zh, text_blocks)
        return {'ok': True, 'translation': segments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn

    print('Starting whisper local service on http://127.0.0.1:8000')
    uvicorn.run(app, host='127.0.0.1', port=8000)
