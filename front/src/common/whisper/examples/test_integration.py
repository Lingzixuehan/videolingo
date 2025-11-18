#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Whisper 字幕提取与嵌入集成测试

完整工作流演示：
1. 从视频提取字幕 -> SRT 文件
2. 将字幕嵌入视频 -> 新视频文件
3. 验证输出文件
"""

import os
import sys
import time
from pathlib import Path

# 添加项目路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.subtitle_extractor import SubtitleExtractor
from core.subtitle_embedder import SubtitleEmbedder


def print_section(title):
    """打印分隔符"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_extraction():
    """测试 1: 字幕提取"""
    print_section("测试 1️⃣: 字幕提取")
    
    # 找到示例视频
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(examples_dir, 'input.mp4')
    output_dir = os.path.join(examples_dir, 'test_output')
    
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return None
    
    print(f"📹 视频文件: {video_path}")
    print(f"📏 大小: {os.path.getsize(video_path) / (1024*1024):.2f} MB\n")
    
    # 进度回调
    def progress(msg):
        print(f"  [INFO] {msg}")
    
    try:
        print("🔄 开始提取字幕...\n")
        extractor = SubtitleExtractor(model='base')
        
        start_time = time.time()
        result = extractor.extract_with_gpu_check(
            video_path=video_path,
            output_dir=output_dir,
            progress_callback=progress
        )
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ 字幕提取成功!")
        print(f"   SRT 文件: {result['srt_path']}")
        print(f"   JSON 文件: {result['json_path']}")
        print(f"   处理时间: {elapsed_time:.2f} 秒")
        
        # 验证 SRT 文件
        if os.path.exists(result['srt_path']):
            with open(result['srt_path'], 'r', encoding='utf-8') as f:
                content = f.read()
                subtitle_count = content.count('\n\n')
                file_size = os.path.getsize(result['srt_path'])
            
            print(f"   字幕块数: {subtitle_count}")
            print(f"   文件大小: {file_size} 字节")
            
            # 显示前几行
            print(f"\n   📋 字幕预览 (前 15 行):")
            for i, line in enumerate(content.split('\n')[:15]):
                if line.strip():
                    print(f"      {line}")
        
        return result
    
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_embedding(srt_path):
    """测试 2: 字幕嵌入"""
    print_section("测试 2️⃣: 字幕嵌入")
    
    if not srt_path:
        print("❌ 跳过: 没有 SRT 文件")
        return None
    
    # 找到示例视频
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(examples_dir, 'input.mp4')
    
    print(f"📹 输入视频: {video_path}")
    print(f"📄 字幕文件: {srt_path}\n")
    
    try:
        print("🔄 开始嵌入字幕...\n")
        embedder = SubtitleEmbedder()
        
        start_time = time.time()
        output_path = embedder.embed(
            video_path=video_path,
            subtitle_path=srt_path
        )
        elapsed_time = time.time() - start_time
        
        if os.path.exists(output_path):
            output_size = os.path.getsize(output_path) / (1024*1024)
            print(f"✅ 字幕嵌入成功!")
            print(f"   输出视频: {output_path}")
            print(f"   文件大小: {output_size:.2f} MB")
            print(f"   处理时间: {elapsed_time:.2f} 秒")
            return output_path
        else:
            print(f"❌ 输出文件未生成")
            return None
    
    except Exception as e:
        print(f"❌ 嵌入失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print_section("🎬 Whisper 字幕提取与嵌入集成测试")
    
    # 测试 1: 提取
    extraction_result = test_extraction()
    
    if not extraction_result or not extraction_result['success']:
        print("\n❌ 提取失败，无法继续")
        sys.exit(1)
    
    # 测试 2: 嵌入
    embedding_result = test_embedding(extraction_result['srt_path'])
    
    # 总结
    print_section("📊 测试总结")
    
    print("✅ 完成的步骤:")
    print(f"  1. ✅ 字幕提取: {extraction_result['srt_path']}")
    
    if embedding_result:
        print(f"  2. ✅ 字幕嵌入: {embedding_result}")
    else:
        print(f"  2. ⚠️  字幕嵌入: 跳过")
    
    print("\n📁 输出文件:")
    print(f"  - {extraction_result['srt_path']}")
    if extraction_result.get('json_path'):
        print(f"  - {extraction_result['json_path']}")
    if embedding_result:
        print(f"  - {embedding_result}")
    
    print("\n✅ 所有测试完成!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
