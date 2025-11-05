"""
字幕解析器单元测试
"""

import sys
import json
import tempfile
from pathlib import Path
import io

# 设置 UTF-8 输出（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.subtitle_parser import SubtitleParser


def test_parse_srt():
    """测试解析 SRT 文件"""
    print("测试: 解析 SRT 文件")

    # 创建临时 SRT 文件
    srt_content = """1
00:00:01,500 --> 00:00:04,200
第一句话。

2
00:00:05,000 --> 00:00:08,000
第二句话。
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
        f.write(srt_content)
        temp_file = f.name

    try:
        parser = SubtitleParser()
        result = parser.parse_subtitle_file(temp_file)

        # 验证结果
        assert result['total_sentences'] == 2, f"期望 2 句，实际 {result['total_sentences']} 句"
        assert result['format'] == 'srt', f"期望格式 'srt'，实际 '{result['format']}'"

        # 验证第一句
        first = result['sentences'][0]
        assert first['start'] == 1.5, f"期望开始时间 1.5s，实际 {first['start']}s"
        assert first['end'] == 4.2, f"期望结束时间 4.2s，实际 {first['end']}s"
        assert first['text'] == '第一句话。', f"文本不匹配"

        # 验证第二句
        second = result['sentences'][1]
        assert second['start'] == 5.0, f"期望开始时间 5.0s，实际 {second['start']}s"
        assert second['end'] == 8.0, f"期望结束时间 8.0s，实际 {second['end']}s"

        print("  ✓ SRT 解析测试通过")
        return True
    except AssertionError as e:
        print(f"  ✗ 测试失败: {e}")
        return False
    finally:
        Path(temp_file).unlink()


def test_parse_ass():
    """测试解析 ASS 文件"""
    print("测试: 解析 ASS 文件")

    # 创建临时 ASS 文件
    ass_content = """[Script Info]
Title: Test

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.50,0:00:04.20,Default,,0,0,0,,第一句话。
Dialogue: 0,0:00:05.00,0:00:08.00,Default,,0,0,0,,{\\b1}加粗文字{\\b0}普通文字。
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8') as f:
        f.write(ass_content)
        temp_file = f.name

    try:
        parser = SubtitleParser()
        result = parser.parse_subtitle_file(temp_file)

        # 验证结果
        assert result['total_sentences'] == 2, f"期望 2 句，实际 {result['total_sentences']} 句"
        assert result['format'] == 'ass', f"期望格式 'ass'，实际 '{result['format']}'"

        # 验证第二句（测试样式标记清理）
        second = result['sentences'][1]
        assert '{' not in second['text'], "文本中不应包含样式标记"
        assert '}' not in second['text'], "文本中不应包含样式标记"
        assert '加粗文字' in second['text'], "应包含去除标记后的文字"

        print("  ✓ ASS 解析测试通过")
        return True
    except AssertionError as e:
        print(f"  ✗ 测试失败: {e}")
        return False
    finally:
        Path(temp_file).unlink()


def test_time_conversion():
    """测试时间转换"""
    print("测试: 时间转换")

    parser = SubtitleParser()

    # 测试毫秒转秒
    assert parser._ms_to_seconds(1500) == 1.5, "1500ms 应该等于 1.5s"
    assert parser._ms_to_seconds(4200) == 4.2, "4200ms 应该等于 4.2s"
    assert parser._ms_to_seconds(0) == 0.0, "0ms 应该等于 0.0s"

    print("  ✓ 时间转换测试通过")
    return True


def test_get_sentence_at_time():
    """测试根据时间查找句子"""
    print("测试: 根据时间查找句子")

    parser = SubtitleParser()
    sentences = [
        {"index": 0, "start": 1.5, "end": 4.2, "text": "第一句"},
        {"index": 1, "start": 5.0, "end": 8.0, "text": "第二句"},
        {"index": 2, "start": 9.0, "end": 12.0, "text": "第三句"},
    ]

    # 测试查找存在的句子
    result1 = parser.get_sentence_at_time(sentences, 2.0)
    assert result1 is not None, "应该找到时间 2.0s 的句子"
    assert result1['text'] == "第一句", "应该是第一句"

    result2 = parser.get_sentence_at_time(sentences, 6.0)
    assert result2 is not None, "应该找到时间 6.0s 的句子"
    assert result2['text'] == "第二句", "应该是第二句"

    # 测试查找不存在的句子
    result3 = parser.get_sentence_at_time(sentences, 4.5)
    assert result3 is None, "时间 4.5s 不应该找到句子"

    print("  ✓ 时间查找测试通过")
    return True


def test_json_output():
    """测试 JSON 输出"""
    print("测试: JSON 输出")

    srt_content = """1
00:00:01,500 --> 00:00:04,200
测试句子。
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
        f.write(srt_content)
        temp_srt = f.name

    try:
        parser = SubtitleParser()

        # 测试自动生成输出文件名
        output_file = parser.parse_and_save_json(temp_srt)
        assert Path(output_file).exists(), "输出文件应该存在"
        assert output_file.endswith('.json'), "输出文件应该是 .json 格式"

        # 验证 JSON 内容
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'sentences' in data, "JSON 应包含 sentences 字段"
            assert 'total_sentences' in data, "JSON 应包含 total_sentences 字段"
            assert 'duration' in data, "JSON 应包含 duration 字段"

        print("  ✓ JSON 输出测试通过")

        # 清理
        Path(output_file).unlink()
        return True
    except AssertionError as e:
        print(f"  ✗ 测试失败: {e}")
        return False
    finally:
        Path(temp_srt).unlink()


def test_invalid_file():
    """测试无效文件处理"""
    print("测试: 无效文件处理")

    parser = SubtitleParser()

    # 测试不存在的文件
    try:
        parser.parse_subtitle_file("nonexistent.srt")
        print("  ✗ 应该抛出 FileNotFoundError")
        return False
    except FileNotFoundError:
        print("  ✓ 正确处理不存在的文件")

    # 测试不支持的格式
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test")
        temp_file = f.name

    try:
        parser.parse_subtitle_file(temp_file)
        print("  ✗ 应该抛出 ValueError")
        Path(temp_file).unlink()
        return False
    except ValueError:
        print("  ✓ 正确处理不支持的格式")
        Path(temp_file).unlink()
        return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行单元测试")
    print("=" * 60)
    print()

    tests = [
        test_time_conversion,
        test_parse_srt,
        test_parse_ass,
        test_get_sentence_at_time,
        test_json_output,
        test_invalid_file,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")
    if passed == total:
        print("所有测试通过！✓")
    else:
        print(f"有 {total - passed} 个测试失败 ✗")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
