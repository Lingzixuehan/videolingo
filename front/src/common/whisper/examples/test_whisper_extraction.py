#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Whisper 字幕提取测试脚本

专门测试 Whisper 从视频提取字幕的功能
- 使用 GPU 加速处理
- 实时显示处理进度
- 详细的性能测试报告

使用方法:
    python test_whisper_extraction.py

依赖:
    - openai-whisper
    - torch (GPU 版本)
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import json

def print_gpu_info():
    """显示 GPU 信息"""
    try:
        import torch
        print("\n" + "=" * 60)
        print("[GPU] GPU 信息")
        print("=" * 60)
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"GPU 名称: {torch.cuda.get_device_name(0)}")
            props = torch.cuda.get_device_properties(0)
            print(f"GPU 内存: {props.total_memory / (1024**3):.2f} GB")
            print(f"CUDA 核心数: {props.multi_processor_count * 128}")
        else:
            print("⚠️  GPU 不可用，将使用 CPU")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"❌ 无法读取 GPU 信息: {e}\n")

def check_dependencies():
    """检查依赖"""
    print("=" * 60)
    print("📋 检查依赖")
    print("=" * 60)
    
    dependencies = {
        'whisper': 'openai-whisper',
        'torch': 'PyTorch',
        'ffmpeg': 'FFmpeg'
    }
    
    missing = []
    
    # 检查 Python 包
    for module, name in list(dependencies.items())[:2]:
        try:
            if module == 'whisper':
                import whisper
                version = whisper.__version__
            elif module == 'torch':
                import torch
                version = torch.__version__
            print(f"✅ {name} - {version}")
        except ImportError:
            print(f"❌ {name} - 未安装")
            missing.append(f"pip install {module if module != 'whisper' else 'openai-whisper'}")
    
    # 检查 FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.decode().split('\n')[0]
            print(f"✅ FFmpeg - {version_line}")
        else:
            print(f"❌ FFmpeg - 无法执行")
            missing.append("pip install ffmpeg-python")
    except FileNotFoundError:
        print(f"❌ FFmpeg - 未安装")
        missing.append("conda install ffmpeg -c conda-forge")
    
    if missing:
        print(f"\n❌ 缺少依赖，请运行:")
        for cmd in missing:
            print(f"   {cmd}")
        return False
    
    print("\n✅ 所有依赖已安装\n")
    return True

def test_whisper_extraction(video_path, output_dir):
    """
    测试 Whisper 字幕提取
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
    
    Returns:
        dict: 包含结果、性能等信息的字典
    """
    print("=" * 60)
    print("🎬 Whisper 字幕提取测试")
    print("=" * 60)
    
    # 验证文件
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return None
    
    video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"\n📹 视频文件: {video_path}")
    print(f"📏 文件大小: {video_size_mb:.2f} MB")
    
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 获取视频信息
    try:
        import ffmpeg
        probe = ffmpeg.probe(video_path)
        video_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
        
        if video_info:
            duration = float(probe['format'].get('duration', 0))
            width = video_info.get('width', 'N/A')
            height = video_info.get('height', 'N/A')
            fps = video_info.get('r_frame_rate', 'N/A')
            print(f"\n🎥 视频信息:")
            print(f"   时长: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
            print(f"   分辨率: {width}x{height}")
            print(f"   帧率: {fps}")
        
        if audio_info:
            sample_rate = audio_info.get('sample_rate', 'N/A')
            channels = audio_info.get('channels', 'N/A')
            print(f"\n🔊 音频信息:")
            print(f"   采样率: {sample_rate} Hz")
            print(f"   通道数: {channels}")
    except Exception as e:
        print(f"\n⚠️ 无法获取视频信息: {e}")
    
    # 运行 Whisper
    print("\n" + "-" * 60)
    print("🔄 运行 Whisper 提取字幕...")
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
    
    print(f"\n📋 命令: {' '.join(cmd)}\n")
    
    try:
        # 实时输出 Whisper 的处理过程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"   {line.rstrip()}")
        
        process.wait()
        elapsed_time = time.time() - start_time
        
        if process.returncode != 0:
            print(f"\n❌ Whisper 执行失败 (返回码: {process.returncode})")
            return None
        
    except Exception as e:
        print(f"\n❌ 执行错误: {e}")
        return None
    
    # 检查输出文件
    video_name = Path(video_path).stem
    srt_path = os.path.join(output_dir, f'{video_name}.srt')
    json_path = os.path.join(output_dir, f'{video_name}.json')
    
    print("\n" + "-" * 60)
    print("📊 处理结果")
    print("-" * 60)
    
    result = {
        'success': False,
        'elapsed_time': elapsed_time,
        'video_file': video_path,
        'video_size_mb': video_size_mb,
        'duration_seconds': duration if 'duration' in locals() else None,
        'srt_path': srt_path,
        'json_path': json_path,
        'srt_exists': os.path.exists(srt_path),
        'json_exists': os.path.exists(json_path),
        'processing_time': elapsed_time,
        'speed': video_size_mb / elapsed_time if elapsed_time > 0 else 0,
    }
    
    if result['srt_exists']:
        print(f"✅ 英文字幕生成: {srt_path}")
        
        # 分析 SRT 文件
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
            srt_lines = len(srt_content.split('\n'))
            srt_size = os.path.getsize(srt_path) / 1024
            subtitle_count = srt_content.count('\n\n')
        
        result['srt_lines'] = srt_lines
        result['srt_size_kb'] = srt_size
        result['subtitle_count'] = subtitle_count
        
        print(f"   字幕块数: {subtitle_count}")
        print(f"   文件大小: {srt_size:.1f} KB")
        print(f"   总行数: {srt_lines}")
    else:
        print(f"❌ 英文字幕生成失败: {srt_path}")
    
    if result['json_exists']:
        print(f"✅ JSON 输出生成: {json_path}")
        result['json_exists'] = True
    else:
        print(f"⚠️ JSON 输出未生成")
    
    # 性能统计
    print(f"\n⏱️  性能统计:")
    print(f"   总耗时: {elapsed_time:.2f} 秒 ({elapsed_time/60:.2f} 分钟)")
    
    if 'duration' in locals() and duration > 0:
        speedup = duration / elapsed_time
        print(f"   视频时长: {duration:.1f} 秒")
        print(f"   处理速度: {speedup:.2f}x (实时速度)")
        result['speedup'] = speedup
    
    print(f"   文件处理速度: {result['speed']:.2f} MB/s")
    
    result['success'] = result['srt_exists']
    
    return result

def test_subtitle_parsing(srt_path):
    """测试字幕解析功能"""
    print("\n" + "=" * 60)
    print("📖 字幕解析测试")
    print("=" * 60)
    
    if not os.path.exists(srt_path):
        print(f"⚠️ 字幕文件不存在: {srt_path}")
        return None
    
    try:
        # 导入模块
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from core.subtitle_parser import SubtitleParser
        
        parser = SubtitleParser()
        result = parser.parse_subtitle_file(srt_path)
        
        if result:
            print(f"✅ 字幕解析成功")
            print(f"   总句数: {result['total_sentences']}")
            print(f"   总时长: {result['duration']:.2f} 秒")
            print(f"   格式: {result['format']}")
            
            # 显示前 3 个句子
            print(f"\n   📋 前 3 个字幕句子:")
            for i, sentence in enumerate(result['sentences'][:3]):
                print(f"      [{i+1}] {sentence['start']:.2f}s - {sentence['end']:.2f}s")
                print(f"          {sentence['text'][:60]}...")
            
            return result
        else:
            print(f"❌ 字幕解析失败")
            return None
    except Exception as e:
        print(f"❌ 异常错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_vocabulary_annotation(srt_path):
    """测试词汇标注功能"""
    print("\n" + "=" * 60)
    print("📚 词汇标注测试")
    print("=" * 60)
    
    if not os.path.exists(srt_path):
        print(f"⚠️ 字幕文件不存在: {srt_path}")
        return None
    
    try:
        # 导入模块
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from core.label import Labeler
        
        # 查找词典
        dict_path = os.path.join(current_dir, 'data', 'ecdict.csv')
        
        if os.path.exists(dict_path):
            print(f"✅ 词典文件已找到: {dict_path}")
            labeler = Labeler(dict_csv_path=dict_path)
        else:
            print(f"⚠️ 词典文件未找到，使用默认词典")
            labeler = Labeler()
        
        # 生成输出路径
        output_path = srt_path.replace('.srt', '-labels.json')
        
        print(f"\n🔄 提取和标注词汇...")
        result = labeler.process_subtitle_file(srt_path, out_json=output_path)
        
        if result:
            print(f"✅ 词汇标注成功")
            print(f"   字幕块数: {len(result.get('blocks', []))}")
            print(f"   提取词汇数: {len(result.get('word_map', {}))}")
            
            # 显示前 10 个词汇
            word_map = result.get('word_map', {})
            if word_map:
                print(f"\n   📚 提取的词汇示例 (前 10 个):")
                for i, (word, info) in enumerate(list(word_map.items())[:10]):
                    trans = info.get('translation', '未知')
                    phonetic = info.get('phonetic', '/')
                    print(f"      [{i+1}] {word} /{phonetic}/ - {trans}")
            
            return result
        else:
            print(f"❌ 词汇标注失败")
            return None
    except Exception as e:
        print(f"❌ 异常错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_report(test_result, parse_result, vocab_result, output_dir):
    """生成测试报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'whisper_extraction': {
            'success': test_result['success'] if test_result else False,
            'elapsed_time_seconds': test_result['elapsed_time'] if test_result else 0,
            'video_file': test_result['video_file'] if test_result else '',
            'video_size_mb': test_result['video_size_mb'] if test_result else 0,
            'processing_speed_mb_per_s': test_result['speed'] if test_result else 0,
            'speedup': test_result.get('speedup', 0),
            'srt_file': test_result['srt_path'] if test_result else '',
            'subtitle_count': test_result.get('subtitle_count', 0),
        },
        'subtitle_parsing': {
            'success': parse_result is not None,
            'total_sentences': parse_result['total_sentences'] if parse_result else 0,
            'total_duration_seconds': parse_result['duration'] if parse_result else 0,
            'format': parse_result['format'] if parse_result else '',
        },
        'vocabulary_annotation': {
            'success': vocab_result is not None,
            'word_count': len(vocab_result.get('word_map', {})) if vocab_result else 0,
            'subtitle_blocks': len(vocab_result.get('blocks', [])) if vocab_result else 0,
        }
    }
    
    report_path = os.path.join(output_dir, 'whisper_test_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report_path

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🎯 Whisper 字幕提取完整测试")
    print("=" * 60 + "\n")
    
    # 打印 GPU 信息
    print_gpu_info()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 找到视频文件
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(examples_dir, 'input.mp4')
    
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        print("请确保 input.mp4 在 examples 目录中")
        sys.exit(1)
    
    output_dir = os.path.join(examples_dir, 'test_output')
    
    # 测试 1: Whisper 字幕提取
    test_result = test_whisper_extraction(video_path, output_dir)
    
    if not test_result or not test_result['success']:
        print("\n❌ Whisper 字幕提取失败，无法继续")
        sys.exit(1)
    
    # 测试 2: 字幕解析
    parse_result = test_subtitle_parsing(test_result['srt_path'])
    
    # 测试 3: 词汇标注
    vocab_result = test_vocabulary_annotation(test_result['srt_path'])
    
    # 生成报告
    report_path = generate_report(test_result, parse_result, vocab_result, output_dir)
    
    # 总结
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    print(f"\n📁 输出文件:")
    print(f"   字幕文件: {test_result['srt_path']}")
    print(f"   JSON 文件: {test_result['json_path']}")
    print(f"   报告文件: {report_path}")
    print(f"\n📊 性能摘要:")
    print(f"   总耗时: {test_result['elapsed_time']:.2f} 秒")
    print(f"   处理速度: {test_result['speed']:.2f} MB/s")
    if test_result.get('speedup'):
        print(f"   实时速度: {test_result['speedup']:.2f}x")
    print("\n" + "=" * 60 + "\n")

if __name__ == '__main__':
    main()
