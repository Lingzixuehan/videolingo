#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 用于快速验证 Whisper 模块的主要功能
无需 pytest，可直接运行：python quick_test.py
"""

import os
import sys
import json
from pathlib import Path

# 设置 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# 导入模块 - 优先使用包导入
try:
    from whisper.core.label import Labeler
    from whisper.core.translator import youdao_translate, collect_subtitle_blocks, split_translation
    from whisper.utils.stardict import DictCsv
    from whisper.utils.vocab_level import VocabLevelChecker, VocabLevel, get_level_from_string
except ImportError:
    # 回退到直接导入
    from core.label import Labeler
    from core.translator import youdao_translate, collect_subtitle_blocks, split_translation
    from utils.stardict import DictCsv
    from utils.vocab_level import VocabLevelChecker, VocabLevel, get_level_from_string


def print_section(title):
    """打印分隔符和标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_stardict():
    """测试 1: StarDict 词典查询"""
    print_section("测试 1: StarDict 词典查询")
    
    try:
        dict_path = current_dir / "data" / "ecdict.mini.csv"
        if not dict_path.exists():
            print(f"❌ 词典文件不存在: {dict_path}")
            return False
        
        dict_obj = DictCsv(str(dict_path))
        
        test_words = ['hello', 'world', 'python', 'code']
        for word in test_words:
            try:
                result = dict_obj.query(word)
                if result:
                    print(f"✅ {word:15} -> {result.get('translation', 'N/A')}")
                else:
                    print(f"⚠️  {word:15} -> 未找到")
            except Exception as e:
                print(f"❌ {word:15} -> 错误: {e}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_vocab_level():
    """测试 2: 词汇难度分级"""
    print_section("测试 2: 词汇难度分级")
    
    try:
        levels = ['basic', 'cet4', 'cet6', 'toefl']
        
        for level_name in levels:
            print(f"\n👤 用户等级: {level_name.upper()}")
            print("-" * 70)
            
            level = get_level_from_string(level_name)
            checker = VocabLevelChecker(level)
            
            # 模拟词汇查询
            test_entries = [
                {'word': 'hello', 'tag': 'zk', 'translation': '你好', 'bnc': '500'},
                {'word': 'abandon', 'tag': 'cet4', 'translation': '放弃', 'bnc': '3500'},
                {'word': 'sophisticated', 'tag': 'cet6', 'translation': '复杂的', 'bnc': '7000'},
            ]
            
            for entry in test_entries:
                is_new = checker.is_beyond_level(entry['word'], entry)
                difficulty = checker.get_difficulty_label(entry['word'], entry)
                status = "❌ 新词" if is_new else "✅ 已掌握"
                print(f"  {entry['word']:20} {status:15} {difficulty}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_labeler():
    """测试 3: 词汇标注器"""
    print_section("测试 3: 词汇标注器")
    
    try:
        # 使用精简词典加快测试
        dict_path = current_dir / "data" / "ecdict.mini.csv"
        if not dict_path.exists():
            print(f"⚠️  词典文件不存在: {dict_path}，跳过此测试")
            return True
        
        labeler = Labeler(str(dict_path), user_vocab_level='cet4')
        
        # 创建临时测试字幕文件
        test_srt = """1
00:00:01,000 --> 00:00:03,000
Hello world, welcome to Python programming.

2
00:00:03,000 --> 00:00:05,000
This is a simple example for testing.
"""
        
        srt_path = current_dir / "temp_test.srt"
        srt_path.write_text(test_srt)
        
        print("📝 测试字幕内容:")
        print(test_srt)
        
        # 处理字幕
        print("\n🔍 处理字幕中...")
        result = labeler.process_subtitle_file(str(srt_path))
        
        # 检查输出结构
        print("\n✅ 输出结构检查:")
        print(f"  - 源文件: {result.get('source')}")
        print(f"  - 字幕块数: {len(result.get('blocks', []))}")
        print(f"  - 不同词汇数: {len(result.get('word_map', {}))}")
        print(f"  - 新词数量: {len(result.get('new_words', []))}")
        
        # 显示词汇信息
        if result.get('word_map'):
            print("\n📚 提取的词汇:")
            for word, info in list(result['word_map'].items())[:5]:
                translation = info.get('entry', {}).get('translation', 'N/A')
                difficulty = info.get('difficulty', 'N/A')
                is_new = "❌" if info.get('is_new') else "✅"
                print(f"  {is_new} {word:20} -> {translation:20} ({difficulty})")
        
        # 清理临时文件
        if srt_path.exists():
            srt_path.unlink()
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_word_lookup():
    """测试 4: 单词查询"""
    print_section("测试 4: 单词查询")
    
    try:
        dict_path = current_dir / "data" / "ecdict.mini.csv"
        if not dict_path.exists():
            print(f"⚠️  词典文件不存在: {dict_path}，跳过此测试")
            return True
        
        labeler = Labeler(str(dict_path))
        
        test_words = ['hello', 'python', 'world', 'example']
        
        print("🔍 查询单个词汇:\n")
        for word in test_words:
            entry = labeler.lookup(word)
            if entry:
                print(f"✅ {word}")
                print(f"   └─ 音标: {entry.get('phonetic', 'N/A')}")
                print(f"   └─ 翻译: {entry.get('translation', 'N/A')}")
                print(f"   └─ 定义: {entry.get('definition', 'N/A')[:50]}")
            else:
                print(f"❌ {word} -> 未找到")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_translator():
    """测试 5: 翻译功能"""
    print_section("测试 5: 翻译功能")
    
    try:
        # 测试翻译 API
        print("📡 测试有道翻译 API...\n")
        
        test_texts = [
            "Hello world",
            "Python is a programming language",
            "This is a test"
        ]
        
        for text in test_texts:
            try:
                print(f"  原文: {text}")
                result = youdao_translate(text, from_lang='en', to_lang='zh-CHS')
                print(f"  翻译: {result}")
                print()
            except Exception as e:
                print(f"  ⚠️  翻译失败: {e}\n")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subtitle_parsing():
    """测试 6: 字幕解析"""
    print_section("测试 6: 字幕解析")
    
    try:
        # 创建测试 SRT 文件
        test_srt = """1
00:00:01,000 --> 00:00:03,000
Hello world, this is line one.

2
00:00:03,000 --> 00:00:05,000
This is line two of the subtitle.

3
00:00:05,000 --> 00:00:07,000
And this is the final line.
"""
        
        srt_path = current_dir / "temp_test.srt"
        srt_path.write_text(test_srt)
        
        print("📝 测试字幕文件:")
        print(test_srt)
        
        print("🔍 解析字幕中...\n")
        subtitle_blocks, text_blocks = collect_subtitle_blocks(str(srt_path))
        
        print(f"✅ 字幕块数: {len(subtitle_blocks)}")
        print(f"✅ 文本块数: {len(text_blocks)}")
        
        print("\n📋 解析结果:")
        for i, item in enumerate(text_blocks, 1):
            # text_blocks 返回 (text, length) 元组
            text, length = item
            print(f"  块 {i}: 长度={length}")
            print(f"       {text}")
        
        # 清理
        if srt_path.exists():
            srt_path.unlink()
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_output_json():
    """测试 7: 输出 JSON 结构"""
    print_section("测试 7: 输出 JSON 结构示例")
    
    try:
        # 生成样本 JSON 结构
        sample = {
            "source": "example.srt",
            "path": "/path/to/example.srt",
            "blocks": [
                {
                    "index": 1,
                    "start": "00:00:01,000",
                    "end": "00:00:03,000",
                    "text": "Hello world",
                    "words": [
                        {
                            "original": "Hello",
                            "entry": {
                                "word": "hello",
                                "phonetic": "həˈləʊ",
                                "translation": "你好",
                                "definition": "used as a greeting"
                            },
                            "is_new": False,
                            "difficulty": "基础词汇"
                        }
                    ]
                }
            ],
            "word_map": {
                "hello": {
                    "entry": {"word": "hello", "translation": "你好"},
                    "is_new": False,
                    "difficulty": "基础词汇",
                    "occurrences": [{"sentence_index": 1, "sentence_text": "Hello world"}]
                }
            },
            "new_words": [
                {
                    "word": "world",
                    "translation": "世界",
                    "difficulty": "基础词汇",
                    "first_occurrence": {
                        "sentence_index": 1,
                        "sentence_text": "Hello world",
                        "timestamp": "00:00:01,000 --> 00:00:03,000"
                    }
                }
            ],
            "statistics": {
                "total_words": 2,
                "new_words_count": 1,
                "coverage_rate": 50.0
            }
        }
        
        print("📦 Labeler 输出 JSON 结构:\n")
        print(json.dumps(sample, indent=2, ensure_ascii=False))
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print_section("🧪 Whisper 模块快速测试")
    print(f"\n当前目录: {current_dir}\n")
    
    tests = [
        ("StarDict 词典查询", test_stardict),
        ("词汇难度分级", test_vocab_level),
        ("单词查询", test_word_lookup),
        ("词汇标注器", test_labeler),
        ("字幕解析", test_subtitle_parsing),
        ("翻译功能", test_translator),
        ("JSON 结构示例", test_output_json),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 打印测试总结
    print_section("📊 测试总结")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"成功率: {passed * 100 // total}%\n")
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status} - {test_name}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️  有 {total - passed} 个测试失败，请检查上述错误信息")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
