#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字幕嵌入核心模块

提供将字幕嵌入视频的核心功能：
1. 使用 FFmpeg 将 SRT 字幕嵌入视频
2. 支持多种字幕格式
3. 自动处理路径转义
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime


class SubtitleEmbedder:
    """字幕嵌入器 - 将字幕嵌入到视频"""
    
    def __init__(self):
        """初始化字幕嵌入器"""
        self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """检查 FFmpeg 是否安装"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError(
                "FFmpeg 未安装或无法访问\n"
                "请安装: pip install ffmpeg-python 或 conda install ffmpeg"
            )
    
    def embed(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: Optional[str] = None,
        force_style: Optional[str] = None
    ) -> str:
        """
        将字幕嵌入视频
        
        Args:
            video_path: 输入视频文件路径
            subtitle_path: 字幕文件路径 (SRT/ASS)
            output_path: 输出视频路径（默认为 xxx_with_subs.mp4）
            force_style: 强制字幕样式（ASS 格式）
        
        Returns:
            输出视频路径
        
        Raises:
            FileNotFoundError: 文件不存在
            RuntimeError: FFmpeg 执行失败
        """
        # 验证文件
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        if not os.path.exists(subtitle_path):
            raise FileNotFoundError(f"字幕文件不存在: {subtitle_path}")
        
        # 设置输出路径
        if output_path is None:
            video_ext = Path(video_path).suffix
            output_path = str(Path(video_path).with_stem(
                Path(video_path).stem + '_with_subs'
            ))
        
        # 准备 FFmpeg 过滤器参数
        # 规范化字幕路径（Windows 路径处理）
        abs_subtitle = os.path.abspath(subtitle_path)
        
        # 转换为 POSIX 风格路径（FFmpeg 更兼容）
        posix_subtitle = abs_subtitle.replace('\\', '/')
        
        # 转义 Windows 驱动器冒号 (C: -> C\:)
        posix_subtitle = re.sub(r'^([A-Za-z]):', r'\1\\:', posix_subtitle)
        
        # 转义单引号
        posix_subtitle = posix_subtitle.replace("'", r"\'")
        
        # 构建 subtitles 过滤器
        if force_style:
            vf_arg = f"subtitles='{posix_subtitle}':force_style='{force_style}'"
        else:
            vf_arg = f"subtitles='{posix_subtitle}'"
        
        # 记录过滤器参数到日志（便于调试）
        log_dir = os.path.dirname(video_path) or os.getcwd()
        log_path = os.path.join(log_dir, 'subtitle_embed.log')
        
        try:
            with open(log_path, 'a', encoding='utf-8') as lf:
                lf.write(f"\n=== {datetime.now().isoformat()} ===\n")
                lf.write(f"Video: {video_path}\n")
                lf.write(f"Subtitle: {subtitle_path}\n")
                lf.write(f"Filter: {vf_arg}\n")
        except:
            pass
        
        # 执行 FFmpeg
        try:
            import ffmpeg
            
            # 使用 ffmpeg-python 库
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path, vf=vf_arg)
            ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)
            
        except Exception as e:
            # 记录错误到日志
            try:
                with open(log_path, 'a', encoding='utf-8') as lf:
                    lf.write(f"ERROR: {str(e)}\n")
                    if hasattr(e, 'stderr'):
                        stderr = e.stderr.decode(errors='replace')
                        lf.write(f"STDERR:\n{stderr}\n")
            except:
                pass
            
            raise RuntimeError(f"字幕嵌入失败: {e}")
        
        # 验证输出
        if not os.path.exists(output_path):
            raise RuntimeError(f"输出文件未生成: {output_path}")
        
        return output_path
    
    def embed_with_custom_style(
        self,
        video_path: str,
        subtitle_path: str,
        font_name: str = 'Arial',
        font_size: int = 24,
        primary_color: str = '&H00FFFFFF',  # 白色
        outline_color: str = '&H00000000',  # 黑色
        output_path: Optional[str] = None
    ) -> str:
        """
        使用自定义样式嵌入字幕
        
        Args:
            video_path: 视频路径
            subtitle_path: 字幕路径
            font_name: 字体名称
            font_size: 字体大小
            primary_color: 主颜色 (ASS 格式)
            outline_color: 边框颜色 (ASS 格式)
            output_path: 输出路径
        
        Returns:
            输出视频路径
        """
        style = (
            f"FontName={font_name},"
            f"FontSize={font_size},"
            f"PrimaryColour={primary_color},"
            f"OutlineColour={outline_color},"
            f"Outline=2"
        )
        
        return self.embed(
            video_path=video_path,
            subtitle_path=subtitle_path,
            output_path=output_path,
            force_style=style
        )


def embed_subtitles(video_path: str, subtitle_path: str) -> str:
    """
    简便函数：将字幕嵌入视频
    
    Args:
        video_path: 视频文件路径
        subtitle_path: 字幕文件路径
    
    Returns:
        输出视频路径
    """
    embedder = SubtitleEmbedder()
    return embedder.embed(video_path, subtitle_path)


if __name__ == '__main__':
    # 测试代码
    import argparse
    
    parser = argparse.ArgumentParser(description='将字幕嵌入视频')
    parser.add_argument('video', help='视频文件路径')
    parser.add_argument('subtitle', help='字幕文件路径')
    parser.add_argument('--output', help='输出视频路径')
    parser.add_argument('--font', default='Arial', help='字体名称')
    parser.add_argument('--size', type=int, default=24, help='字体大小')
    
    args = parser.parse_args()
    
    try:
        embedder = SubtitleEmbedder()
        
        print(f"[INFO] 嵌入字幕到视频...")
        print(f"  视频: {args.video}")
        print(f"  字幕: {args.subtitle}")
        
        output = embedder.embed(
            video_path=args.video,
            subtitle_path=args.subtitle,
            output_path=args.output
        )
        
        print(f"\n✅ 成功!")
        print(f"输出: {output}")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
