"""
词汇难度分级系统测试
"""

import json
from vocab_level import VocabLevelChecker, VocabLevel, get_level_from_string


def test_level_checker():
    """测试词汇难度检查器"""
    print("=" * 60)
    print("测试 1: 词汇难度检查器基本功能")
    print("=" * 60)

    # 模拟不同等级的用户
    levels_to_test = ['basic', 'cet4', 'cet6', 'toefl']

    # 测试词汇（带模拟的词库数据）
    test_words = [
        {
            'word': 'hello',
            'entry': {'word': 'hello', 'tag': 'zk gk', 'translation': '你好', 'bnc': '500'}
        },
        {
            'word': 'abandon',
            'entry': {'word': 'abandon', 'tag': 'cet4 cet6', 'translation': '放弃', 'bnc': '3500'}
        },
        {
            'word': 'sophisticated',
            'entry': {'word': 'sophisticated', 'tag': 'cet6 toefl', 'translation': '复杂的', 'bnc': '7000'}
        },
        {
            'word': 'paradigm',
            'entry': {'word': 'paradigm', 'tag': 'gre', 'translation': '范例', 'bnc': '15000'}
        },
    ]

    for level_str in levels_to_test:
        print(f"\n用户等级: {level_str.upper()}")
        print("-" * 60)

        checker = VocabLevelChecker(get_level_from_string(level_str))

        for word_data in test_words:
            word = word_data['word']
            entry = word_data['entry']

            is_new = checker.is_beyond_level(word, entry)
            difficulty = checker.get_difficulty_label(word, entry)

            status = "❌ 超纲" if is_new else "✅ 已掌握"
            print(f"  {word:20} - {status:10} - {difficulty}")


def test_tag_parsing():
    """测试标签解析"""
    print("\n" + "=" * 60)
    print("测试 2: 标签解析功能")
    print("=" * 60)

    checker = VocabLevelChecker(VocabLevel.CET4)

    test_tags = [
        "cet4 cet6",
        "zk gk",
        "toefl ielts",
        "gre",
        "",
        "cet4"
    ]

    for tag in test_tags:
        levels = checker.parse_word_tags(tag)
        level_names = [l.value for l in levels]
        print(f"  Tag: '{tag:20}' -> {level_names}")


def test_frequency_based_check():
    """测试基于词频的判断"""
    print("\n" + "=" * 60)
    print("测试 3: 基于词频的难度判断（无标签词汇）")
    print("=" * 60)

    checker = VocabLevelChecker(VocabLevel.CET4)

    # 模拟没有标签但有词频的词
    test_words = [
        {'word': 'common_word', 'entry': {'word': 'common_word', 'tag': '', 'bnc': '1000'}},
        {'word': 'medium_word', 'entry': {'word': 'medium_word', 'tag': '', 'bnc': '6000'}},
        {'word': 'rare_word', 'entry': {'word': 'rare_word', 'tag': '', 'bnc': '15000'}},
    ]

    for word_data in test_words:
        word = word_data['word']
        entry = word_data['entry']

        is_new = checker.is_beyond_level(word, entry)
        difficulty = checker.get_difficulty_label(word, entry)

        status = "❌ 超纲" if is_new else "✅ 已掌握"
        bnc = entry['bnc']
        print(f"  {word:20} (BNC={bnc:6}) - {status:10} - {difficulty}")


def test_output_structure():
    """测试输出数据结构示例"""
    print("\n" + "=" * 60)
    print("测试 4: 输出 JSON 结构示例")
    print("=" * 60)

    # 模拟 label.py 的输出结构
    sample_output = {
        "source": "example.srt",
        "path": "/path/to/example.srt",
        "blocks": [
            {
                "index": 1,
                "start": "00:00:01,000",
                "end": "00:00:03,500",
                "text": "Hello, this is a sophisticated example.",
                "words": [
                    {
                        "original": "Hello",
                        "entry": {"word": "hello", "translation": "你好"},
                        "is_new": False,
                        "difficulty": "基础词汇"
                    },
                    {
                        "original": "sophisticated",
                        "entry": {"word": "sophisticated", "translation": "复杂的"},
                        "is_new": True,
                        "difficulty": "六级词汇"
                    }
                ]
            }
        ],
        "word_map": {
            "hello": {
                "entry": {"word": "hello", "translation": "你好"},
                "is_new": False,
                "difficulty": "基础词汇",
                "occurrences": [
                    {"sentence_index": 1, "sentence_text": "Hello, this is a sophisticated example."}
                ]
            },
            "sophisticated": {
                "entry": {"word": "sophisticated", "translation": "复杂的"},
                "is_new": True,
                "difficulty": "六级词汇",
                "occurrences": [
                    {"sentence_index": 1, "sentence_text": "Hello, this is a sophisticated example."}
                ]
            }
        },
        "new_words": [
            {
                "word": "sophisticated",
                "translation": "复杂的",
                "difficulty": "六级词汇",
                "first_occurrence": {
                    "sentence_index": 1,
                    "sentence_text": "Hello, this is a sophisticated example.",
                    "timestamp": "00:00:01,000 --> 00:00:03,500"
                }
            }
        ],
        "statistics": {
            "total_words": 2,
            "new_words_count": 1,
            "coverage_rate": 50.0
        }
    }

    print(json.dumps(sample_output, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    test_level_checker()
    test_tag_parsing()
    test_frequency_based_check()
    test_output_structure()

    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)
