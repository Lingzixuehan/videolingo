"""
Videolingo Whisper Module
字幕处理、翻译、词汇标注一体化模块

主要功能：
- 音频转字幕 (Whisper)
- 字幕翻译 (Youdao API)
- 词汇标注 (Dictionary)
- 字幕嵌入 (FFmpeg)
- 字幕解析 (SubtitleParser)
"""

__version__ = "0.1.0"
__author__ = "Videolingo Team"

from .core.label import Labeler
from .core.translator import youdao_translate, collect_subtitle_blocks, split_translation
from .core.subtitle_parser import SubtitleParser
from .utils.stardict import DictCsv

__all__ = [
    'Labeler',
    'youdao_translate',
    'collect_subtitle_blocks',
    'split_translation',
    'SubtitleParser',
    'DictCsv',
]
