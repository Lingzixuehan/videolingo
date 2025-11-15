"""
字幕解析器演示脚本
展示如何使用 SubtitleParser 解析字幕文件
"""

import sys
import json
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.subtitle_parser import SubtitleParser


def main():
    """主函数"""
    print("=" * 60)
    print("字幕解析器演示")
    print("=" * 60)
    print()

    # 创建解析器实例
    parser = SubtitleParser()

    # 获取示例文件路径
    examples_dir = Path(__file__).parent
    srt_file = examples_dir / "example.srt"
    ass_file = examples_dir / "example.ass"

    # 解析 SRT 文件
    print("1. 解析 SRT 文件:")
    print(f"   文件: {srt_file.name}")
    print("-" * 60)

    try:
        srt_result = parser.parse_subtitle_file(str(srt_file))
        print(f"   总句数: {srt_result['total_sentences']}")
        print(f"   总时长: {srt_result['duration']} 秒")
        print(f"   格式: {srt_result['format']}")
        print()
        print("   前3句内容:")
        for sentence in srt_result['sentences'][:3]:
            print(f"   [{sentence['index']}] {sentence['video_timestamp']}")
            print(f"       时间: {sentence['start']}s - {sentence['end']}s")
            print(f"       文本: {sentence['text']}")
            print()

        # 保存为 JSON
        output_file = parser.parse_and_save_json(str(srt_file))
        print(f"   已保存到: {output_file}")
        print()
    except Exception as e:
        print(f"   错误: {e}")
        print()

    # 解析 ASS 文件
    print("2. 解析 ASS 文件:")
    print(f"   文件: {ass_file.name}")
    print("-" * 60)

    try:
        ass_result = parser.parse_subtitle_file(str(ass_file))
        print(f"   总句数: {ass_result['total_sentences']}")
        print(f"   总时长: {ass_result['duration']} 秒")
        print(f"   格式: {ass_result['format']}")
        print()
        print("   所有句子:")
        for sentence in ass_result['sentences']:
            print(f"   [{sentence['index']}] {sentence['video_timestamp']}")
            print(f"       时间: {sentence['start']}s - {sentence['end']}s")
            print(f"       文本: {sentence['text']}")
            print()

        # 保存为 JSON
        output_file = parser.parse_and_save_json(str(ass_file))
        print(f"   已保存到: {output_file}")
        print()
    except Exception as e:
        print(f"   错误: {e}")
        print()

    # 演示查找特定时间的句子
    print("3. 查找特定时间的句子:")
    print("-" * 60)
    test_times = [2.0, 5.5, 10.0]
    for time_point in test_times:
        sentence = parser.get_sentence_at_time(srt_result['sentences'], time_point)
        if sentence:
            print(f"   时间 {time_point}s 的句子:")
            print(f"   文本: {sentence['text']}")
        else:
            print(f"   时间 {time_point}s 没有找到对应的句子")
        print()

    print("=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
