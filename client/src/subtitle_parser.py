"""
字幕解析器模块
使用 pysubs2 解析 srt/ass 等格式的字幕文件，并按句对齐输出 JSON 数据
"""

import json
from typing import Dict, List, Any, Optional
import pysubs2
from pathlib import Path


class SubtitleParser:
    """字幕解析器类"""

    def __init__(self):
        """初始化字幕解析器"""
        self.supported_formats = ['.srt', '.ass', '.ssa', '.sub', '.vtt']

    def _ms_to_seconds(self, milliseconds: int) -> float:
        """
        将毫秒转换为秒

        Args:
            milliseconds: 毫秒数

        Returns:
            秒数（保留3位小数）
        """
        return round(milliseconds / 1000.0, 3)

    def _format_timestamp(self, start_ms: int, end_ms: int, format_type: str = 'srt') -> str:
        """
        格式化时间戳

        Args:
            start_ms: 开始时间（毫秒）
            end_ms: 结束时间（毫秒）
            format_type: 格式类型（srt/ass）

        Returns:
            格式化的时间戳字符串
        """
        if format_type.lower() == 'srt':
            start_h = start_ms // 3600000
            start_m = (start_ms % 3600000) // 60000
            start_s = (start_ms % 60000) // 1000
            start_ms_part = start_ms % 1000

            end_h = end_ms // 3600000
            end_m = (end_ms % 3600000) // 60000
            end_s = (end_ms % 60000) // 1000
            end_ms_part = end_ms % 1000

            return f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms_part:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms_part:03d}"
        else:  # ass format
            start_h = start_ms // 3600000
            start_m = (start_ms % 3600000) // 60000
            start_s = (start_ms % 60000) // 1000
            start_cs = (start_ms % 1000) // 10  # centiseconds

            end_h = end_ms // 3600000
            end_m = (end_ms % 3600000) // 60000
            end_s = (end_ms % 60000) // 1000
            end_cs = (end_ms % 1000) // 10

            return f"{start_h:01d}:{start_m:02d}:{start_s:02d}.{start_cs:02d} --> {end_h:01d}:{end_m:02d}:{end_s:02d}.{end_cs:02d}"

    def _clean_text(self, text: str) -> str:
        """
        清理字幕文本，移除格式标记

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        # 移除 ASS/SSA 格式的样式标记
        import re
        text = re.sub(r'\{[^}]*\}', '', text)
        # 移除多余的空格和换行
        text = ' '.join(text.split())
        return text.strip()

    def parse_subtitle_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析字幕文件

        Args:
            file_path: 字幕文件路径

        Returns:
            包含句级数据的字典

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        path = Path(file_path)

        # 检查文件是否存在
        if not path.exists():
            raise FileNotFoundError(f"字幕文件不存在: {file_path}")

        # 检查文件格式
        if path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"不支持的字幕格式: {path.suffix}。支持的格式: {', '.join(self.supported_formats)}")

        # 使用 pysubs2 加载字幕
        subs = pysubs2.load(file_path)

        # 提取句级数据
        sentences = []
        for idx, event in enumerate(subs):
            # 跳过注释或空行
            if event.is_comment or not event.text.strip():
                continue

            sentence = {
                "index": idx,
                "start": self._ms_to_seconds(event.start),
                "end": self._ms_to_seconds(event.end),
                "text": self._clean_text(event.text),
                "video_timestamp": self._format_timestamp(event.start, event.end, path.suffix[1:])
            }
            sentences.append(sentence)

        # 重新索引（去除跳过的行后）
        for new_idx, sentence in enumerate(sentences):
            sentence["index"] = new_idx

        # 计算总时长
        total_duration = 0
        if sentences:
            total_duration = sentences[-1]["end"]

        result = {
            "sentences": sentences,
            "total_sentences": len(sentences),
            "duration": total_duration,
            "source_file": str(path.name),
            "format": path.suffix[1:]
        }

        return result

    def parse_and_save_json(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        解析字幕文件并保存为 JSON

        Args:
            input_file: 输入字幕文件路径
            output_file: 输出 JSON 文件路径（可选，默认为输入文件名.json）

        Returns:
            输出文件路径
        """
        # 解析字幕
        result = self.parse_subtitle_file(input_file)

        # 确定输出文件路径
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix('.json'))

        # 保存为 JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return output_file

    def get_sentence_at_time(self, sentences: List[Dict[str, Any]], time_seconds: float) -> Optional[Dict[str, Any]]:
        """
        获取指定时间点的句子

        Args:
            sentences: 句子列表
            time_seconds: 时间点（秒）

        Returns:
            匹配的句子，如果没有找到则返回 None
        """
        for sentence in sentences:
            if sentence["start"] <= time_seconds <= sentence["end"]:
                return sentence
        return None
