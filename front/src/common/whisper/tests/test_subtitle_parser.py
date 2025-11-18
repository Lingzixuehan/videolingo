#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字幕解析模块 (SubtitleParser) 单元测试

运行方式：
  pytest tests/test_subtitle_parser.py -v
  python -m pytest tests/test_subtitle_parser.py -v
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from core.subtitle_parser import SubtitleParser


class TestSubtitleParser:
    """字幕解析器基本功能测试"""
    
    @pytest.fixture
    def parser(self):
        """创建解析器实例"""
        return SubtitleParser()
    
    @pytest.fixture
    def sample_srt_file(self):
        """创建测试 SRT 文件"""
        content = """1
00:00:01,000 --> 00:00:03,000
Hello world.

2
00:00:03,000 --> 00:00:05,000
This is a test.

3
00:00:05,000 --> 00:00:07,000
Good bye!
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        
        # 清理
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_parser_initialization(self, parser):
        """测试解析器初始化"""
        assert parser is not None
        assert parser.supported_formats == ['.srt', '.ass', '.ssa', '.sub', '.vtt']
        print("✅ 解析器初始化成功")
    
    def test_ms_to_seconds(self, parser):
        """测试毫秒转秒"""
        assert parser._ms_to_seconds(0) == 0.0
        assert parser._ms_to_seconds(1000) == 1.0
        assert parser._ms_to_seconds(1500) == 1.5
        assert parser._ms_to_seconds(3661000) == 3661.0
        print("✅ 毫秒转秒成功")
    
    def test_format_timestamp_srt(self, parser):
        """测试 SRT 时间戳格式化"""
        timestamp = parser._format_timestamp(1000, 3000, 'srt')
        assert timestamp == "00:00:01,000 --> 00:00:03,000"
        
        timestamp = parser._format_timestamp(61000, 63500, 'srt')
        assert timestamp == "00:01:01,000 --> 00:01:03,500"
        
        print("✅ SRT 时间戳格式化成功")
    
    def test_format_timestamp_ass(self, parser):
        """测试 ASS 时间戳格式化"""
        timestamp = parser._format_timestamp(1000, 3000, 'ass')
        assert timestamp == "0:00:01.00 --> 0:00:03.00"
        
        timestamp = parser._format_timestamp(61000, 63500, 'ass')
        assert timestamp == "0:01:01.00 --> 0:01:03.50"
        
        print("✅ ASS 时间戳格式化成功")
    
    def test_clean_text(self, parser):
        """测试文本清理"""
        # 测试移除 ASS 样式标记
        text = "{\\b1}Bold{\\b0} Normal"
        cleaned = parser._clean_text(text)
        assert cleaned == "Bold Normal"
        
        # 测试移除多余空格
        text = "  Multiple   spaces  "
        cleaned = parser._clean_text(text)
        assert cleaned == "Multiple spaces"
        
        # 测试组合
        text = "  {\\i1}Italic{\\i0}  Text  "
        cleaned = parser._clean_text(text)
        assert cleaned == "Italic Text"
        
        print("✅ 文本清理成功")
    
    def test_parse_subtitle_file(self, parser, sample_srt_file):
        """测试解析 SRT 文件"""
        result = parser.parse_subtitle_file(sample_srt_file)
        
        assert result is not None
        assert 'sentences' in result
        assert 'total_sentences' in result
        assert 'duration' in result
        assert 'source_file' in result
        assert 'format' in result
        
        # 检查句子数
        assert result['total_sentences'] == 3
        assert len(result['sentences']) == 3
        
        # 检查第一个句子
        first = result['sentences'][0]
        assert first['index'] == 0
        assert first['start'] == 1.0
        assert first['end'] == 3.0
        assert first['text'] == 'Hello world.'
        
        print(f"✅ 解析 SRT 文件成功: {result['total_sentences']} 句")
    
    def test_parse_subtitle_file_not_found(self, parser):
        """测试文件不存在"""
        with pytest.raises(FileNotFoundError):
            parser.parse_subtitle_file('/nonexistent/file.srt')
        
        print("✅ 文件不存在检查成功")
    
    def test_parse_subtitle_file_invalid_format(self, parser):
        """测试不支持的文件格式"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                parser.parse_subtitle_file(temp_path)
            print("✅ 格式检查成功")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_parse_and_save_json(self, parser, sample_srt_file):
        """测试解析并保存为 JSON"""
        # 解析并保存
        output_file = parser.parse_and_save_json(sample_srt_file)
        
        # 检查输出文件
        assert os.path.exists(output_file)
        assert output_file.endswith('.json')
        
        # 检查 JSON 内容
        import json
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'sentences' in data
        assert len(data['sentences']) == 3
        
        # 清理
        os.unlink(output_file)
        
        print("✅ 解析并保存 JSON 成功")
    
    def test_get_sentence_at_time(self, parser, sample_srt_file):
        """测试按时间查找句子"""
        result = parser.parse_subtitle_file(sample_srt_file)
        sentences = result['sentences']
        
        # 第一个句子（1.0-3.0）
        sentence = parser.get_sentence_at_time(sentences, 2.0)
        assert sentence is not None
        assert sentence['text'] == 'Hello world.'
        
        # 第二个句子（3.0-5.0）
        sentence = parser.get_sentence_at_time(sentences, 4.0)
        assert sentence is not None
        assert sentence['text'] == 'This is a test.'
        
        # 没有句子的时间
        sentence = parser.get_sentence_at_time(sentences, 10.0)
        assert sentence is None
        
        print("✅ 按时间查找成功")


class TestSubtitleParserIntegration:
    """集成测试"""
    
    def test_workflow(self):
        """测试完整工作流"""
        parser = SubtitleParser()
        
        # 创建测试文件
        content = """1
00:00:01,000 --> 00:00:02,000
Hello

2
00:00:02,000 --> 00:00:03,000
World
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # 解析
            result = parser.parse_subtitle_file(temp_path)
            print(f"✅ 解析完成: {result['total_sentences']} 句")
            
            # 保存
            output_file = parser.parse_and_save_json(temp_path)
            print(f"✅ 保存完成: {output_file}")
            
            # 查询
            for sentence in result['sentences']:
                t = (sentence['start'] + sentence['end']) / 2
                found = parser.get_sentence_at_time(result['sentences'], t)
                print(f"✅ 在 {t}s 找到: {found['text']}")
            
            # 清理
            os.unlink(output_file)
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_subtitle_file(self):
        """测试空字幕文件"""
        parser = SubtitleParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = f.name
        
        try:
            result = parser.parse_subtitle_file(temp_path)
            assert result['total_sentences'] == 0
            print("✅ 空文件处理成功")
        finally:
            os.unlink(temp_path)
    
    def test_multiline_subtitle(self):
        """测试多行字幕"""
        parser = SubtitleParser()
        
        content = """1
00:00:01,000 --> 00:00:03,000
Line one
Line two
Line three
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = parser.parse_subtitle_file(temp_path)
            assert result['total_sentences'] == 1
            # 多行应该被合并
            assert 'Line one' in result['sentences'][0]['text']
            print("✅ 多行字幕处理成功")
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
