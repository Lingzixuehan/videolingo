"""Core functionality - 核心功能模块

包含以下核心模块：
- subtitle_extractor: 字幕提取（核心功能）
- subtitle_embedder: 字幕嵌入（核心功能）
- subtitle_parser: 字幕解析和处理
- label: 词汇标注和提取
- translator: 字幕翻译
"""

from .subtitle_extractor import SubtitleExtractor, extract_subtitles_from_video
from .subtitle_embedder import SubtitleEmbedder, embed_subtitles
from .subtitle_parser import SubtitleParser
from .label import Labeler
from .translator import youdao_translate, collect_subtitle_blocks, split_translation

__all__ = [
    # 核心功能（生产就绪）
    'SubtitleExtractor',
    'extract_subtitles_from_video',
    'SubtitleEmbedder',
    'embed_subtitles',
    # 其他功能
    'SubtitleParser',
    'Labeler',
    'youdao_translate',
    'collect_subtitle_blocks',
    'split_translation',
]
