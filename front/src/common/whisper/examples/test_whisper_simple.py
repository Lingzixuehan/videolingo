#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Whisper extraction test - simplified version without emoji"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

# Add project path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_whisper():
    print("\n" + "="*60)
    print("Whisper Subtitle Extraction Test")
    print("="*60 + "\n")
    
    # GPU Info
    try:
        import torch
        print("[INFO] GPU Information:")
        print(f"  PyTorch: {torch.__version__}")
        print(f"  CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA: {torch.version.cuda}")
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to read GPU info: {e}\n")
    
    # Check dependencies
    print("[INFO] Checking dependencies...")
    try:
        import whisper
        print(f"  Whisper: {whisper.__version__} - OK")
    except:
        print("  Whisper: MISSING")
        return False
    
    try:
        import torch
        print(f"  PyTorch: {torch.__version__} - OK")
    except:
        print("  PyTorch: MISSING")
        return False
    
    print()
    
    # Video file
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(examples_dir, 'input.mp4')
    
    if not os.path.exists(video_path):
        print(f"[ERROR] Video not found: {video_path}\n")
        return False
    
    print(f"[INFO] Video file: {video_path}")
    print(f"       Size: {os.path.getsize(video_path) / (1024*1024):.2f} MB\n")
    
    # Output directory
    output_dir = os.path.join(examples_dir, 'test_output')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Run Whisper
    print("[INFO] Running Whisper extraction...")
    print("-" * 60)
    
    start_time = time.time()
    
    cmd = [
        sys.executable, '-m', 'whisper',
        video_path,
        '--model', 'base',
        '--language', 'English',
        '--task', 'translate',
        '--output_format', 'srt',
        '--output_format', 'json',
        '--output_dir', output_dir,
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"  {line.rstrip()}")
        
        process.wait()
        elapsed_time = time.time() - start_time
        
        if process.returncode != 0:
            print(f"\n[ERROR] Whisper failed (return code: {process.returncode})\n")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] Execution error: {e}\n")
        return False
    
    # Check output
    print("-" * 60)
    print("[INFO] Processing results:\n")
    
    video_name = Path(video_path).stem
    srt_path = os.path.join(output_dir, f'{video_name}.srt')
    json_path = os.path.join(output_dir, f'{video_name}.json')
    
    if os.path.exists(srt_path):
        print(f"[OK] Subtitle file: {srt_path}")
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
            subtitle_count = srt_content.count('\n\n')
            srt_size = os.path.getsize(srt_path) / 1024
        
        print(f"     Subtitles: {subtitle_count}")
        print(f"     Size: {srt_size:.1f} KB\n")
        
        # Show preview
        lines = srt_content.split('\n')
        print("[INFO] Subtitle preview (first 10 lines):")
        for line in lines[:10]:
            if line.strip():
                print(f"  {line}")
    else:
        print(f"[ERROR] Subtitle file not found\n")
        return False
    
    if os.path.exists(json_path):
        print(f"\n[OK] JSON file: {json_path}\n")
    
    # Performance
    print("[INFO] Performance:")
    print(f"  Total time: {elapsed_time:.2f} seconds")
    print(f"  Processing speed: {os.path.getsize(video_path) / (1024*1024) / elapsed_time:.2f} MB/s\n")
    
    # Test parsing
    try:
        from core.subtitle_parser import SubtitleParser
        print("[INFO] Testing SubtitleParser...")
        parser = SubtitleParser()
        result = parser.parse_subtitle_file(srt_path)
        if result:
            print(f"[OK] Parse success - {result['total_sentences']} sentences, {result['duration']:.1f}s total")
            for i, s in enumerate(result['sentences'][:3]):
                print(f"     [{i+1}] {s['start']:.1f}s: {s['text'][:50]}...")
    except Exception as e:
        print(f"[ERROR] Parse test failed: {e}")
    
    # Test vocabulary
    try:
        print("\n[INFO] Testing vocabulary annotation...")
        from core.label import Labeler
        dict_path = os.path.join(current_dir, 'data', 'ecdict.csv')
        if os.path.exists(dict_path):
            labeler = Labeler(dict_csv_path=dict_path)
        else:
            labeler = Labeler()
        
        labels_path = srt_path.replace('.srt', '-labels.json')
        result = labeler.process_subtitle_file(srt_path, out_json=labels_path)
        if result:
            word_count = len(result.get('word_map', {}))
            print(f"[OK] Vocabulary annotation success - {word_count} words")
            word_map = result.get('word_map', {})
            for i, (word, info) in enumerate(list(word_map.items())[:5]):
                trans = info.get('translation', '?')
                print(f"     [{i+1}] {word} - {trans}")
    except Exception as e:
        print(f"[ERROR] Vocabulary test failed: {e}")
    
    print("\n" + "="*60)
    print("Test completed successfully!")
    print("="*60 + "\n")
    
    return True

if __name__ == '__main__':
    success = test_whisper()
    sys.exit(0 if success else 1)
