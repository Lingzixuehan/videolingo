#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 用于测试自己的字幕文件
使用方法：python quick_test.py your_subtitle.srt
"""

import sys
import json
from pathlib import Path
import io

# Windows UTF-8 支持
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.subtitle_parser import SubtitleParser


def main():
    if len(sys.argv) < 2:
        print("使用方法：python quick_test.py <字幕文件路径>")
        print("\n示例：")
        print("  python quick_test.py examples/example.srt")
        print("  python quick_test.py examples/example.ass")
        print("  python quick_test.py /path/to/your/subtitle.srt")
        sys.exit(1)

    subtitle_file = sys.argv[1]

    # 检查文件是否存在
    if not Path(subtitle_file).exists():
        print(f"❌ 错误：文件不存在 - {subtitle_file}")
        sys.exit(1)

    print("=" * 60)
    print(f"正在解析：{subtitle_file}")
    print("=" * 60)
    print()

    try:
        # 创建解析器
        parser = SubtitleParser()

        # 解析字幕
        result = parser.parse_subtitle_file(subtitle_file)

        # 显示基本信息
        print(f"✓ 解析成功！")
        print(f"  格式：{result['format']}")
        print(f"  总句数：{result['total_sentences']}")
        print(f"  总时长：{result['duration']} 秒")
        print()

        # 显示前5句
        print("前 5 句内容：")
        print("-" * 60)
        for sentence in result['sentences'][:5]:
            print(f"[{sentence['index']}] {sentence['video_timestamp']}")
            print(f"    时间：{sentence['start']}s - {sentence['end']}s")
            print(f"    文本：{sentence['text']}")
            print()

        if result['total_sentences'] > 5:
            print(f"... 还有 {result['total_sentences'] - 5} 句")
            print()

        # 保存为 JSON
        output_file = parser.parse_and_save_json(subtitle_file)
        print(f"✓ JSON 已保存到：{output_file}")
        print()

        # 显示 JSON 内容（格式化）
        print("JSON 输出预览：")
        print("-" * 60)
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 只显示前500个字符
            if len(content) > 500:
                print(content[:500] + "...")
            else:
                print(content)

        print()
        print("=" * 60)
        print("✓ 测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
