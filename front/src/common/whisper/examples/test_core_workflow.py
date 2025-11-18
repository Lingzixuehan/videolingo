#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Whisper 核心功能测试脚本

测试字幕提取和嵌入功能
使用 examples/input.mp4 进行测试
"""

import os
import sys
from pathlib import Path

# 添加项目路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.video_workflow import VideoWorkflow


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  Whisper 字幕提取与嵌入测试")
    print("=" * 70 + "\n")
    
    # 查找测试视频
    examples_dir = os.path.join(current_dir, 'examples')
    video_path = os.path.join(examples_dir, 'input.mp4')
    
    if not os.path.exists(video_path):
        print(f"❌ 测试视频不存在: {video_path}")
        print("请确保 input.mp4 在 examples 目录中")
        return False
    
    print(f"✅ 找到测试视频: {video_path}")
    video_size = os.path.getsize(video_path) / (1024 * 1024)
    print(f"   文件大小: {video_size:.2f} MB\n")
    
    # 设置输出目录
    output_dir = os.path.join(examples_dir, 'test_output')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"📁 输出目录: {output_dir}\n")
    
    # 创建工作流
    print("🔧 初始化工作流...")
    try:
        workflow = VideoWorkflow(
            whisper_model='base',
            user_vocab_level='cet4'
        )
        print("✅ 工作流初始化成功\n")
    except Exception as e:
        print(f"❌ 工作流初始化失败: {e}\n")
        return False
    
    # 进度回调
    def print_progress(msg: str):
        print(f"  {msg}")
    
    # 执行处理
    print("🚀 开始处理视频...\n")
    print("-" * 70)
    
    try:
        result = workflow.process_video(
            video_path=video_path,
            output_dir=output_dir,
            embed_subtitle=True,
            annotate_vocabulary=True,
            progress_callback=print_progress
        )
        
        print("-" * 70)
        print()
        
        # 显示结果
        if result['success']:
            print("=" * 70)
            print("  ✅ 测试成功！")
            print("=" * 70)
            
            print("\n📊 处理结果:\n")
            
            # 字幕文件
            if result['srt_path'] and os.path.exists(result['srt_path']):
                srt_size = os.path.getsize(result['srt_path']) / 1024
                print(f"  ✅ SRT 字幕: {os.path.basename(result['srt_path'])}")
                print(f"     大小: {srt_size:.1f} KB")
                
                # 统计字幕块数
                with open(result['srt_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    blocks = content.count('\n\n')
                print(f"     字幕块: {blocks} 个")
            
            # JSON 文件
            if result['json_path'] and os.path.exists(result['json_path']):
                json_size = os.path.getsize(result['json_path']) / 1024
                print(f"\n  ✅ JSON 输出: {os.path.basename(result['json_path'])}")
                print(f"     大小: {json_size:.1f} KB")
            
            # 解析结果
            if result['parse_result']:
                pr = result['parse_result']
                print(f"\n  ✅ 字幕解析:")
                print(f"     总句数: {pr['total_sentences']}")
                print(f"     总时长: {pr['duration']:.1f} 秒")
                print(f"     格式: {pr['format']}")
            
            # 词汇标注
            if result['labels_path'] and os.path.exists(result['labels_path']):
                labels_size = os.path.getsize(result['labels_path']) / 1024
                print(f"\n  ✅ 词汇标注: {os.path.basename(result['labels_path'])}")
                print(f"     大小: {labels_size:.1f} KB")
                
                if result['label_result']:
                    lr = result['label_result']
                    word_count = len(lr.get('word_map', {}))
                    new_words = len(lr.get('new_words', []))
                    stats = lr.get('statistics', {})
                    coverage = stats.get('coverage_rate', 0)
                    
                    print(f"     总词数: {word_count}")
                    print(f"     新词数: {new_words}")
                    print(f"     覆盖率: {coverage:.1f}%")
            
            # 嵌入视频
            if result['output_video_path'] and os.path.exists(result['output_video_path']):
                video_size = os.path.getsize(result['output_video_path']) / (1024 * 1024)
                print(f"\n  ✅ 嵌入视频: {os.path.basename(result['output_video_path'])}")
                print(f"     大小: {video_size:.2f} MB")
            
            print("\n" + "=" * 70)
            print(f"  📁 所有文件已保存到: {output_dir}")
            print("=" * 70 + "\n")
            
            return True
        else:
            print("=" * 70)
            print("  ❌ 测试失败")
            print("=" * 70)
            
            if 'error' in result:
                print(f"\n错误信息: {result['error']}\n")
            
            return False
    
    except Exception as e:
        print("-" * 70)
        print()
        print("=" * 70)
        print("  ❌ 测试异常")
        print("=" * 70)
        print(f"\n错误: {e}\n")
        
        import traceback
        traceback.print_exc()
        
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
