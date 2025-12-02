#!/usr/bin/env python3
"""
Quick standalone script to run the Whisper-based SubtitleExtractor on a test video.

Place this file in the project root (`videolingo`) and run:
  python extract_test.py

Options:
  --video PATH   path to video file to process (optional)
  --model NAME   whisper model to use (tiny|base|small|medium|large). Default: tiny

This script will try to import the local `front/src/common/whisper` package
by adding it to `sys.path`. It writes outputs to `front/whisper_test_output`.
"""
import os
import sys
import argparse
import traceback
from datetime import datetime

BASE = os.path.dirname(__file__)
WHISPER_LOCAL = os.path.join(BASE, 'front', 'src', 'common')
if WHISPER_LOCAL not in sys.path:
    sys.path.insert(0, WHISPER_LOCAL)


def now():
    return datetime.now().strftime('%H:%M:%S')


def find_default_video():
    candidates = [
        os.path.join(BASE, 'front', 'public', 'videos', 'test.mp4'),
        os.path.join(BASE, 'front', 'src', 'common', 'whisper', 'examples', 'input.mp4'),
        os.path.join(BASE, 'front', 'src', 'common', 'whisper', 'examples', 'input_with_subs.mp4'),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def main():
    parser = argparse.ArgumentParser(description='Run local Whisper SubtitleExtractor on test video')
    parser.add_argument('--video', '-v', help='Path to video file (optional)')
    parser.add_argument('--model', '-m', default='tiny', help='Whisper model to use (default: tiny)')
    args = parser.parse_args()

    video = args.video or find_default_video()
    if not video:
        print('[ERROR] No video found. Place a test.mp4 at front/public/videos/test.mp4 or pass --video PATH')
        sys.exit(2)

    if not os.path.exists(video):
        print(f'[ERROR] Video not found: {video}')
        sys.exit(3)

    try:
        # lazy import from local whisper module
        from whisper.core.subtitle_extractor import SubtitleExtractor
    except Exception as e:
        print('[ERROR] Failed to import local whisper module. Make sure dependencies are installed and path is correct.')
        print('Detail:', e)
        # Provide actionable hints for missing dependencies
        req_path = os.path.join(WHISPER_LOCAL, 'whisper', 'requirements.txt')
        print('\nQuick fixes:')
        print(' - Ensure you run inside the project virtualenv:')
        print('     .\\.venv\\Scripts\\Activate.ps1')
        print(' - Install the minimal Python packages required by the local whisper helpers:')
        print('     pip install pysubs2')
        if os.path.exists(req_path):
            print(f" - Or install the full list listed by the project: pip install -r {req_path}")
        print(' - The heavy ML deps (whisper / torch / ffmpeg) are optional for a quick import check, but required to actually run extraction:')
        print('     pip install -U "git+https://github.com/openai/whisper.git"')
        print('     pip install torch --index-url https://download.pytorch.org/whl/cpu')
        print(' - If you need a small quick test, use the `--model tiny` model to avoid long downloads.')
        traceback.print_exc()
        sys.exit(4)

    outdir = os.path.join(BASE, 'front', 'whisper_test_output')
    os.makedirs(outdir, exist_ok=True)

    def progress_cb(msg):
        # SubtitleExtractor passes textual output lines; print them with timestamp
        try:
            text = str(msg)
        except Exception:
            text = repr(msg)
        print(f'[{now()}] {text}', flush=True)

    print(f'[{now()}] Starting extraction for: {video} (model={args.model})')
    try:
        # Creating the extractor may import torch and other heavy libs which
        # on Windows can raise OSError (DLL initialization failure). Catch that
        # specifically and print actionable remediation steps.
        extractor = SubtitleExtractor(model=args.model)
    except OSError as e:
        print(f'[{now()}] Extraction failed during initialization: {e}')
        print('\nThis looks like a Windows DLL initialization error (often WinError 1114) when importing PyTorch.')
        print('Common fixes:')
        print('  1) Use the CPU-only PyTorch wheel instead of a CUDA build:')
        print('       python -m pip uninstall -y torch torchvision torchaudio')
        print('       python -m pip install --index-url https://download.pytorch.org/whl/cpu torch')
        print('  2) Install the Microsoft Visual C++ Redistributable (x64) if missing:')
        print('       https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist')
        print('  3) On laptops, set the power profile to "High performance" or disable GPU switching in vendor tools; some drivers fail to initialize CUDA runtime under certain power modes.')
        print('  4) If you do not need GPU, installing the CPU wheel (step 1) usually resolves the issue quickly.')
        print('\nAfter reinstalling, verify with:')
        print('  python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"')
        traceback.print_exc()
        sys.exit(6)
    except Exception as e:
        print(f'[{now()}] Extraction initialization failed: {e}')
        traceback.print_exc()
        sys.exit(5)

    try:
        res = extractor.extract_with_gpu_check(video_path=video, output_dir=outdir, progress_callback=progress_cb)
        print(f'[{now()}] Extraction finished successfully.')
        print('Result:')
        for k, v in res.items():
            print(f'  {k}: {v}')
        print(f'Output directory: {outdir}')
        sys.exit(0)
    except Exception as e:
        print(f'[{now()}] Extraction failed during processing: {e}')
        traceback.print_exc()
        sys.exit(7)


if __name__ == '__main__':
    main()
