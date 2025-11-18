#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字幕提取核心模块

提供视频字幕提取的核心功能：
1. 使用 Whisper 从视频提取字幕
2. 自动生成 SRT 格式字幕文件
3. 支持进度回调
4. GPU 加速支持
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Callable, Dict, Any


class SubtitleExtractor:
    """字幕提取器 - 使用 Whisper 从视频提取字幕"""
    
    def __init__(self, model: str = 'base'):
        """
        初始化字幕提取器
        
        Args:
            model: Whisper 模型大小 ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model = model
        self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """检查依赖是否安装"""
        try:
            import whisper
            import torch
            return True
        except ImportError as e:
            raise RuntimeError(
                f"缺少依赖: {e}\n"
                "请运行: pip install openai-whisper torch"
            )
    
    def extract(
        self,
        video_path: str,
        output_dir: Optional[str] = None,
        language: str = 'English',
        task: str = 'translate',
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        从视频提取字幕
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录（默认为视频所在目录）
            language: 音频语言
            task: 任务类型 ('transcribe' 或 'translate')
            progress_callback: 进度回调函数
        
        Returns:
            包含提取结果的字典:
            {
                'success': bool,
                'srt_path': str,
                'json_path': str,
                'video_path': str,
                'output_dir': str
            }
        """
        # 验证视频文件
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.dirname(video_path)
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 构建 Whisper 命令
        cmd = [
            sys.executable, '-m', 'whisper',
            video_path,
            '--model', self.model,
            '--language', language,
            '--task', task,
            '--output_format', 'srt',  # 强制生成 SRT
            '--output_format', 'json',  # 同时生成 JSON
            '--output_dir', output_dir,
        ]
        
        if progress_callback:
            progress_callback(f"开始提取字幕 (模型: {self.model})...")
        
        # 执行 Whisper
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 实时读取输出
            for line in iter(process.stdout.readline, ''):
                if line.strip() and progress_callback:
                    progress_callback(line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                raise RuntimeError(f"Whisper 执行失败 (返回码: {process.returncode})")
        
        except Exception as e:
            raise RuntimeError(f"字幕提取失败: {e}")
        
        # 检查输出文件
        video_name = Path(video_path).stem
        srt_path = os.path.join(output_dir, f'{video_name}.srt')
        json_path = os.path.join(output_dir, f'{video_name}.json')
        
        if not os.path.exists(srt_path):
            raise RuntimeError(
                f"SRT 文件未生成: {srt_path}\n"
                "Whisper 可能处理失败"
            )
        
        if progress_callback:
            progress_callback(f"字幕提取完成: {srt_path}")
        
        return {
            'success': True,
            'srt_path': srt_path,
            'json_path': json_path if os.path.exists(json_path) else None,
            'video_path': video_path,
            'output_dir': output_dir
        }
    
    def extract_with_gpu_check(
        self,
        video_path: str,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        提取字幕并显示 GPU 信息
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            progress_callback: 进度回调函数
        
        Returns:
            提取结果字典
        """
        # 检查 GPU
        try:
            import torch
            if torch.cuda.is_available() and progress_callback:
                gpu_name = torch.cuda.get_device_name(0)
                progress_callback(f"使用 GPU: {gpu_name}")
            elif progress_callback:
                progress_callback("使用 CPU 处理")
        except:
            pass
        
        return self.extract(
            video_path=video_path,
            output_dir=output_dir,
            progress_callback=progress_callback
        )


def extract_subtitles_from_video(
    video_path: str,
    output_dir: Optional[str] = None,
    model: str = 'base'
) -> str:
    """
    简便函数：从视频提取字幕
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        model: Whisper 模型
    
    Returns:
        生成的 SRT 文件路径
    """
    extractor = SubtitleExtractor(model=model)
    result = extractor.extract(video_path, output_dir)
    return result['srt_path']


if __name__ == '__main__':
    # 测试代码
    import argparse
    
    parser = argparse.ArgumentParser(description='从视频提取字幕')
    parser.add_argument('video', help='视频文件路径')
    parser.add_argument('--model', default='base', help='Whisper 模型')
    parser.add_argument('--output', help='输出目录')
    
    args = parser.parse_args()
    
    def print_progress(msg: str):
        print(f"[INFO] {msg}")
    
    try:
        extractor = SubtitleExtractor(model=args.model)
        result = extractor.extract(
            video_path=args.video,
            output_dir=args.output,
            progress_callback=print_progress
        )
        
        print(f"\n✅ 成功!")
        print(f"SRT 文件: {result['srt_path']}")
        if result['json_path']:
            print(f"JSON 文件: {result['json_path']}")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
