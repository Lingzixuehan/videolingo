#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字幕解析模块集成示例

演示如何使用 SubtitleParser 与其他模块集成：
1. 解析 SRT 字幕
2. 提取词汇（使用 Labeler）
3. 翻译字幕（使用 youdao_translate）
4. 生成结构化输出
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from core.subtitle_parser import SubtitleParser
from core.label import Labeler
from core.translator import youdao_translate


def example_1_basic_parsing():
    """示例 1: 基本解析"""
    print("\n" + "=" * 70)
    print("示例 1: 基本字幕解析")
    print("=" * 70)
    
    parser = SubtitleParser()
    
    # 创建示例 SRT 文件
    sample_srt = """1
00:00:01,000 --> 00:00:03,000
Hello, welcome to the tutorial.

2
00:00:03,000 --> 00:00:05,000
Today we'll learn Python programming.

3
00:00:05,000 --> 00:00:07,000
Let's get started!
"""
    
    # 保存到临时文件
    temp_file = "temp_example.srt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(sample_srt)
    
    try:
        # 解析
        result = parser.parse_subtitle_file(temp_file)
        
        print(f"\n📊 解析结果：")
        print(f"  总句数: {result['total_sentences']}")
        print(f"  总时长: {result['duration']} 秒")
        print(f"  格式: {result['format'].upper()}")
        
        print(f"\n📝 句子列表：")
        for sentence in result['sentences']:
            print(f"  [{sentence['index']}] {sentence['start']}s - {sentence['end']}s")
            print(f"      {sentence['text']}")
    
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def example_2_parse_and_save():
    """示例 2: 解析并保存为 JSON"""
    print("\n" + "=" * 70)
    print("示例 2: 解析并保存为 JSON")
    print("=" * 70)
    
    parser = SubtitleParser()
    
    # 创建示例文件
    sample_srt = """1
00:00:01,000 --> 00:00:02,500
Introduction

2
00:00:02,500 --> 00:00:04,000
Main content
"""
    
    temp_file = "temp_example.srt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(sample_srt)
    
    try:
        # 解析并保存
        json_file = parser.parse_and_save_json(temp_file)
        print(f"\n✅ 已保存到: {json_file}")
        
        # 显示 JSON 内容
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📋 JSON 结构：")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 清理
        if os.path.exists(json_file):
            os.unlink(json_file)
    
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def example_3_time_query():
    """示例 3: 按时间查询句子"""
    print("\n" + "=" * 70)
    print("示例 3: 按时间查询句子")
    print("=" * 70)
    
    parser = SubtitleParser()
    
    sample_srt = """1
00:00:01,000 --> 00:00:03,000
First sentence

2
00:00:03,000 --> 00:00:05,000
Second sentence

3
00:00:05,000 --> 00:00:07,000
Third sentence
"""
    
    temp_file = "temp_example.srt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(sample_srt)
    
    try:
        result = parser.parse_subtitle_file(temp_file)
        
        # 在不同时间查询
        test_times = [1.5, 3.5, 5.5, 8.0]
        
        print(f"\n⏱️  时间查询：")
        for t in test_times:
            sentence = parser.get_sentence_at_time(result['sentences'], t)
            if sentence:
                print(f"  {t}s -> {sentence['text']}")
            else:
                print(f"  {t}s -> (无字幕)")
    
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def example_4_with_labeler():
    """示例 4: 与 Labeler 集成（词汇提取）"""
    print("\n" + "=" * 70)
    print("示例 4: 与 Labeler 集成")
    print("=" * 70)
    
    parser = SubtitleParser()
    
    sample_srt = """1
00:00:01,000 --> 00:00:03,000
Hello world

2
00:00:03,000 --> 00:00:05,000
Python programming
"""
    
    temp_file = "temp_example.srt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(sample_srt)
    
    try:
        # 解析字幕
        result = parser.parse_subtitle_file(temp_file)
        print(f"\n✅ 字幕解析完成: {result['total_sentences']} 句")
        
        # 尝试与 Labeler 结合
        try:
            labeler = Labeler()
            print(f"✅ Labeler 初始化成功")
            
            # 查询词汇
            for sentence in result['sentences'][:1]:  # 只处理第一个句子作为示例
                words = sentence['text'].split()
                print(f"\n📚 词汇查询 ({sentence['text']})：")
                for word in words[:2]:  # 只查询前两个词
                    entry = labeler.lookup(word)
                    if entry:
                        print(f"  {word}: {entry.get('translation', 'N/A')}")
                    else:
                        print(f"  {word}: (未找到)")
        
        except Exception as e:
            print(f"⚠️  Labeler 集成示例失败: {e}")
            print(f"   （这是正常的，如果词典文件不可用）")
    
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def example_5_with_translator():
    """示例 5: 与翻译模块集成"""
    print("\n" + "=" * 70)
    print("示例 5: 与翻译模块集成")
    print("=" * 70)
    
    parser = SubtitleParser()
    
    sample_srt = """1
00:00:01,000 --> 00:00:03,000
Hello world

2
00:00:03,000 --> 00:00:05,000
Python is great
"""
    
    temp_file = "temp_example.srt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(sample_srt)
    
    try:
        # 解析字幕
        result = parser.parse_subtitle_file(temp_file)
        print(f"\n✅ 字幕解析完成: {result['total_sentences']} 句")
        
        # 尝试翻译
        print(f"\n🌐 翻译示例：")
        for sentence in result['sentences']:
            text = sentence['text']
            try:
                # 翻译第一个句子
                if sentence['index'] == 0:
                    translation = youdao_translate(text)
                    print(f"  原文: {text}")
                    print(f"  翻译: {translation}")
                    break
            except Exception as e:
                print(f"  ⚠️  翻译失败: {e}")
                print(f"     （需要网络连接和有效的 API Key）")
                break
    
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def example_6_complete_workflow():
    """示例 6: 完整工作流"""
    print("\n" + "=" * 70)
    print("示例 6: 完整工作流")
    print("=" * 70)
    
    parser = SubtitleParser()
    
    sample_srt = """1
00:00:01,000 --> 00:00:02,500
Introduction

2
00:00:02,500 --> 00:00:04,000
Main content

3
00:00:04,000 --> 00:00:05,500
Conclusion
"""
    
    temp_srt = "temp_example.srt"
    temp_json = "temp_example.json"
    
    with open(temp_srt, 'w', encoding='utf-8') as f:
        f.write(sample_srt)
    
    try:
        print(f"\n📝 步骤 1: 解析字幕")
        result = parser.parse_subtitle_file(temp_srt)
        print(f"  ✓ 解析完成: {result['total_sentences']} 句")
        
        print(f"\n📊 步骤 2: 保存为 JSON")
        json_file = parser.parse_and_save_json(temp_srt)
        print(f"  ✓ 保存完成: {json_file}")
        
        print(f"\n🔍 步骤 3: 统计信息")
        print(f"  总句数: {result['total_sentences']}")
        print(f"  总时长: {result['duration']} 秒")
        print(f"  平均句长: {result['duration'] / result['total_sentences']:.1f} 秒")
        
        print(f"\n📋 步骤 4: 句子详情")
        for sentence in result['sentences']:
            duration = sentence['end'] - sentence['start']
            print(f"  [{sentence['index']}] {duration:.1f}秒 - {sentence['text']}")
        
        print(f"\n✅ 完整工作流完成！")
        
        # 清理
        if os.path.exists(json_file):
            os.unlink(json_file)
    
    finally:
        if os.path.exists(temp_srt):
            os.unlink(temp_srt)


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🎬 字幕解析模块集成示例")
    print("=" * 70)
    
    # 运行所有示例
    example_1_basic_parsing()
    example_2_parse_and_save()
    example_3_time_query()
    example_4_with_labeler()
    example_5_with_translator()
    example_6_complete_workflow()
    
    print("\n" + "=" * 70)
    print("✅ 所有示例完成！")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
