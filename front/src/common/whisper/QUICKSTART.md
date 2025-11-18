#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速开始指南 - Whisper 字幕提取和嵌入

这个脚本展示了如何使用 Whisper 模块的核心功能
"""

print("""
╔════════════════════════════════════════════════════════════╗
║  Whisper 字幕提取和嵌入 - 快速开始指南                     ║
╚════════════════════════════════════════════════════════════╝
""")

print("""
📚 目录
1. 字幕提取 (SubtitleExtractor)
2. 字幕嵌入 (SubtitleEmbedder)
3. 完整工作流

""")

print("""
═══════════════════════════════════════════════════════════

1️⃣  字幕提取 - 从视频生成 SRT 文件

""")

print("""
方式 A: 使用便捷函数（推荐）
─────────────────────────────

from whisper.core import extract_subtitles_from_video

# 一行代码提取字幕
srt_path = extract_subtitles_from_video(
    'video.mp4',
    output_dir='./output',
    model='base'
)

print(f"字幕已保存: {srt_path}")
""")

print("""
方式 B: 使用类方法（更多控制）
────────────────────────────

from whisper.core import SubtitleExtractor

extractor = SubtitleExtractor(model='base')

# 定义进度回调
def on_progress(msg):
    print(f"[进度] {msg}")

# 执行提取
result = extractor.extract_with_gpu_check(
    video_path='video.mp4',
    output_dir='./output',
    progress_callback=on_progress
)

# 使用结果
srt_path = result['srt_path']
json_path = result['json_path']

print(f"✅ SRT: {srt_path}")
print(f"✅ JSON: {json_path}")
""")

print("""
═══════════════════════════════════════════════════════════

2️⃣  字幕嵌入 - 将字幕嵌入到视频

""")

print("""
方式 A: 使用便捷函数（推荐）
─────────────────────────────

from whisper.core import embed_subtitles

# 一行代码嵌入字幕
output_video = embed_subtitles('input.mp4', 'subtitles.srt')

print(f"输出视频: {output_video}")
""")

print("""
方式 B: 使用类方法（自定义样式）
────────────────────────────

from whisper.core import SubtitleEmbedder

embedder = SubtitleEmbedder()

# 标准嵌入
output = embedder.embed(
    video_path='input.mp4',
    subtitle_path='subtitles.srt'
)

# 自定义字幕样式
output = embedder.embed_with_custom_style(
    video_path='input.mp4',
    subtitle_path='subtitles.srt',
    font_name='Arial',
    font_size=28,
    primary_color='&H00FFFFFF',   # 白色
    outline_color='&H00000000'    # 黑色
)

print(f"✅ 输出: {output}")
""")

print("""
═══════════════════════════════════════════════════════════

3️⃣  完整工作流 - 提取 + 嵌入 + 标注

""")

print("""
from whisper.core import (
    SubtitleExtractor,
    SubtitleEmbedder,
    Labeler
)

# 步骤 1: 提取字幕
print("1️⃣  提取字幕...")
extractor = SubtitleExtractor(model='base')
result = extractor.extract('video.mp4', './output')
srt_path = result['srt_path']

# 步骤 2: 嵌入字幕
print("2️⃣  嵌入字幕...")
embedder = SubtitleEmbedder()
output_video = embedder.embed('video.mp4', srt_path)

# 步骤 3: 标注词汇
print("3️⃣  标注词汇...")
labeler = Labeler()
labels = labeler.process_subtitle_file(srt_path)

print(f"✅ 完成!")
print(f"   视频: {output_video}")
print(f"   词汇: {len(labels['word_map'])} 个")
""")

print("""
═══════════════════════════════════════════════════════════

📋 常用参数

字幕提取 (extract):
  - video_path: 视频文件路径
  - output_dir: 输出目录（默认为视频目录）
  - language: 音频语言 (默认: 'English')
  - task: 'transcribe' 或 'translate' (默认: 'translate')
  - progress_callback: 进度回调函数

字幕嵌入 (embed):
  - video_path: 输入视频路径
  - subtitle_path: 字幕文件路径
  - output_path: 输出视频路径（默认: xxx_with_subs.mp4）
  - force_style: 强制样式（ASS 格式）

═══════════════════════════════════════════════════════════

🧪 运行测试

集成测试 (推荐):
  cd examples
  python test_integration.py

简单提取测试:
  cd examples
  python test_whisper_simple.py

完整工作流:
  cd examples
  python test_video_workflow.py

═══════════════════════════════════════════════════════════

💡 提示

1. 首次运行会下载 Whisper 模型（139 MB）
2. GPU 加速可以 4.7 倍加快处理速度
3. 支持多种模型: tiny, base, small, medium, large
4. SRT 和 JSON 格式同时生成

═══════════════════════════════════════════════════════════

📖 更多信息

- README.md - 完整文档
- examples/ - 示例代码
- core/ - 核心模块源代码

═══════════════════════════════════════════════════════════
""")
