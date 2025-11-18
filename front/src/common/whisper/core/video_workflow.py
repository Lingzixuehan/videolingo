#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的视频字幕处理工作流

整合所有功能：
1. 字幕提取 (Whisper)
2. 字幕解析 (SubtitleParser)
3. 词汇标注 (Labeler)
4. 字幕嵌入 (SubtitleEmbedder)

使用示例:
    python video_workflow.py input.mp4
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Callable

# 添加项目路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.subtitle_extractor import SubtitleExtractor
from core.subtitle_embedder import SubtitleEmbedder
from core.subtitle_parser import SubtitleParser
from core.label import Labeler


class VideoWorkflow:
    """视频字幕处理完整工作流"""
    
    def __init__(
        self,
        whisper_model: str = 'base',
        dict_path: Optional[str] = None,
        user_vocab_level: str = 'cet4'
    ):
        """
        初始化工作流
        
        Args:
            whisper_model: Whisper 模型大小
            dict_path: 词典文件路径
            user_vocab_level: 用户词汇等级
        """
        self.extractor = SubtitleExtractor(model=whisper_model)
        self.embedder = SubtitleEmbedder()
        self.parser = SubtitleParser()
        
        # 初始化 Labeler
        if dict_path and os.path.exists(dict_path):
            self.labeler = Labeler(
                dict_csv_path=dict_path,
                user_vocab_level=user_vocab_level
            )
        else:
            self.labeler = Labeler(user_vocab_level=user_vocab_level)
    
    def process_video(
        self,
        video_path: str,
        output_dir: Optional[str] = None,
        embed_subtitle: bool = True,
        annotate_vocabulary: bool = True,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        处理视频完整流程
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            embed_subtitle: 是否嵌入字幕到视频
            annotate_vocabulary: 是否标注词汇
            progress_callback: 进度回调函数
        
        Returns:
            处理结果字典
        """
        result = {
            'success': False,
            'video_path': video_path,
            'srt_path': None,
            'json_path': None,
            'labels_path': None,
            'output_video_path': None,
            'parse_result': None,
            'label_result': None
        }
        
        try:
            # 步骤 1: 提取字幕
            if progress_callback:
                progress_callback("步骤 1/4: 提取字幕...")
            
            extract_result = self.extractor.extract(
                video_path=video_path,
                output_dir=output_dir,
                progress_callback=progress_callback
            )
            
            result['srt_path'] = extract_result['srt_path']
            result['json_path'] = extract_result['json_path']
            
            if progress_callback:
                progress_callback(f"✅ 字幕提取完成: {result['srt_path']}")
            
            # 步骤 2: 解析字幕
            if progress_callback:
                progress_callback("步骤 2/4: 解析字幕...")
            
            parse_result = self.parser.parse_subtitle_file(result['srt_path'])
            result['parse_result'] = parse_result
            
            if progress_callback:
                total = parse_result['total_sentences']
                duration = parse_result['duration']
                progress_callback(
                    f"✅ 字幕解析完成: {total} 句, {duration:.1f}秒"
                )
            
            # 步骤 3: 词汇标注
            if annotate_vocabulary:
                if progress_callback:
                    progress_callback("步骤 3/4: 标注词汇...")
                
                labels_path = result['srt_path'].replace('.srt', '-labels.json')
                label_result = self.labeler.process_subtitle_file(
                    result['srt_path'],
                    out_json=labels_path
                )
                
                result['labels_path'] = labels_path
                result['label_result'] = label_result
                
                if progress_callback and label_result:
                    word_count = len(label_result.get('word_map', {}))
                    new_words = len(label_result.get('new_words', []))
                    progress_callback(
                        f"✅ 词汇标注完成: {word_count} 词, {new_words} 新词"
                    )
            else:
                if progress_callback:
                    progress_callback("步骤 3/4: 跳过词汇标注")
            
            # 步骤 4: 嵌入字幕
            if embed_subtitle:
                if progress_callback:
                    progress_callback("步骤 4/4: 嵌入字幕到视频...")
                
                output_video = self.embedder.embed(
                    video_path=video_path,
                    subtitle_path=result['srt_path']
                )
                
                result['output_video_path'] = output_video
                
                if progress_callback:
                    progress_callback(f"✅ 字幕嵌入完成: {output_video}")
            else:
                if progress_callback:
                    progress_callback("步骤 4/4: 跳过字幕嵌入")
            
            result['success'] = True
            
            if progress_callback:
                progress_callback("\n✅ 所有步骤完成!")
            
            return result
        
        except Exception as e:
            if progress_callback:
                progress_callback(f"\n❌ 处理失败: {e}")
            
            result['error'] = str(e)
            return result


def process_video(
    video_path: str,
    output_dir: Optional[str] = None,
    model: str = 'base'
) -> Dict[str, Any]:
    """
    简便函数：处理视频完整流程
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        model: Whisper 模型
    
    Returns:
        处理结果字典
    """
    workflow = VideoWorkflow(whisper_model=model)
    
    def print_progress(msg: str):
        print(f"[INFO] {msg}")
    
    return workflow.process_video(
        video_path=video_path,
        output_dir=output_dir,
        progress_callback=print_progress
    )


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='视频字幕处理完整工作流',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 基础用法
    python video_workflow.py input.mp4
    
    # 指定输出目录
    python video_workflow.py input.mp4 --output ./output
    
    # 使用大模型
    python video_workflow.py input.mp4 --model large
    
    # 跳过字幕嵌入
    python video_workflow.py input.mp4 --no-embed
    
    # 跳过词汇标注
    python video_workflow.py input.mp4 --no-annotate
        """
    )
    
    parser.add_argument('video', help='视频文件路径')
    parser.add_argument('--output', help='输出目录')
    parser.add_argument('--model', default='base', 
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper 模型大小')
    parser.add_argument('--dict', help='词典文件路径')
    parser.add_argument('--level', default='cet4',
                       choices=['basic', 'cet4', 'cet6', 'toefl', 'ielts', 'gre'],
                       help='用户词汇等级')
    parser.add_argument('--no-embed', action='store_true',
                       help='不嵌入字幕到视频')
    parser.add_argument('--no-annotate', action='store_true',
                       help='不标注词汇')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("视频字幕处理工作流")
    print("=" * 60)
    print(f"视频: {args.video}")
    print(f"模型: {args.model}")
    print(f"词汇等级: {args.level}")
    print("=" * 60)
    print()
    
    try:
        # 创建工作流
        workflow = VideoWorkflow(
            whisper_model=args.model,
            dict_path=args.dict,
            user_vocab_level=args.level
        )
        
        # 处理视频
        def print_progress(msg: str):
            print(f"[INFO] {msg}")
        
        result = workflow.process_video(
            video_path=args.video,
            output_dir=args.output,
            embed_subtitle=not args.no_embed,
            annotate_vocabulary=not args.no_annotate,
            progress_callback=print_progress
        )
        
        # 打印结果
        print("\n" + "=" * 60)
        print("处理结果")
        print("=" * 60)
        
        if result['success']:
            print("✅ 状态: 成功")
            print(f"\n📁 输出文件:")
            print(f"  字幕文件: {result['srt_path']}")
            if result['json_path']:
                print(f"  JSON 文件: {result['json_path']}")
            if result['labels_path']:
                print(f"  词汇标注: {result['labels_path']}")
            if result['output_video_path']:
                print(f"  嵌入视频: {result['output_video_path']}")
            
            if result['parse_result']:
                pr = result['parse_result']
                print(f"\n📊 字幕统计:")
                print(f"  总句数: {pr['total_sentences']}")
                print(f"  总时长: {pr['duration']:.1f} 秒")
            
            if result['label_result']:
                lr = result['label_result']
                word_count = len(lr.get('word_map', {}))
                new_words = len(lr.get('new_words', []))
                print(f"\n📚 词汇统计:")
                print(f"  总词数: {word_count}")
                print(f"  新词数: {new_words}")
        else:
            print("❌ 状态: 失败")
            if 'error' in result:
                print(f"错误: {result['error']}")
        
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
