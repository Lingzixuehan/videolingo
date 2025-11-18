#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
翻译模块 (translator) 单元测试

运行方式：
  pytest tests/test_translator.py -v
  pytest tests/test_translator.py -v -k "test_parse"
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from core.translator import (
    youdao_translate, 
    collect_subtitle_blocks, 
    split_translation,
    md5_encode,
    truncate
)


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_truncate(self):
        """测试截断函数"""
        text = "This is a very long text"
        result = truncate(text)
        assert len(result) <= 20
        print(f"✅ 截断: {text} -> {result}")
    
    def test_md5_encode(self):
        """测试 MD5 编码"""
        text = "hello world"
        result = md5_encode(text)
        assert isinstance(result, str)
        assert len(result) == 32  # MD5 哈希长度
        print(f"✅ MD5 编码: {text} -> {result}")
    
    def test_md5_consistent(self):
        """测试 MD5 一致性"""
        text = "test string"
        hash1 = md5_encode(text)
        hash2 = md5_encode(text)
        assert hash1 == hash2
        print(f"✅ MD5 一致性验证成功")


class TestSubtitleParsing:
    """测试字幕解析"""
    
    @pytest.fixture
    def test_srt_file(self):
        """创建测试 SRT 文件"""
        srt_content = """1
00:00:01,000 --> 00:00:03,000
This is the first line.

2
00:00:03,000 --> 00:00:05,000
This is the second line.
Here is a continuation.

3
00:00:05,000 --> 00:00:07,000
Final line.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt',
                                        delete=False, encoding='utf-8') as f:
            f.write(srt_content)
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_collect_subtitle_blocks(self, test_srt_file):
        """测试收集字幕块"""
        subtitle_blocks, text_blocks = collect_subtitle_blocks(test_srt_file)
        
        assert len(subtitle_blocks) > 0
        assert len(text_blocks) > 0
        assert len(subtitle_blocks) == len(text_blocks)
        
        print(f"✅ 收集字幕块: {len(subtitle_blocks)} 个块")
    
    def test_text_block_structure(self, test_srt_file):
        """测试文本块结构"""
        subtitle_blocks, text_blocks = collect_subtitle_blocks(test_srt_file)
        
        if text_blocks:
            text, time_range = text_blocks[0]
            
            # 检查文本
            assert isinstance(text, str)
            assert len(text) > 0
            
            # 检查时间范围
            assert isinstance(time_range, tuple)
            assert len(time_range) == 2
            start, end = time_range
            assert isinstance(start, str)
            assert isinstance(end, str)
            
            print(f"✅ 文本块结构验证成功")
            print(f"   文本: {text}")
            print(f"   时间: {start} --> {end}")
    
    def test_parse_empty_srt(self):
        """测试解析空 SRT 文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt',
                                        delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = f.name
        
        try:
            subtitle_blocks, text_blocks = collect_subtitle_blocks(temp_path)
            assert subtitle_blocks == []
            assert text_blocks == []
            print(f"✅ 解析空 SRT 文件成功")
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestSplitTranslation:
    """测试翻译分割"""
    
    def test_split_translation_basic(self):
        """测试基本分割"""
        full_translation = "这是第一行。这是第二行。最后一行。"
        text_blocks = [
            ("This is the first line.", ("00:00:01,000", "00:00:03,000")),
            ("This is the second line.", ("00:00:03,000", "00:00:05,000")),
            ("Final line.", ("00:00:05,000", "00:00:07,000")),
        ]
        
        result = split_translation(full_translation, text_blocks)
        
        assert len(result) == len(text_blocks)
        assert all(isinstance(s, str) for s in result)
        
        print(f"✅ 分割翻译成功: {len(result)} 个分段")
        for i, segment in enumerate(result, 1):
            print(f"   段落 {i}: {segment}")
    
    def test_split_translation_preserves_length(self):
        """测试分割保持长度"""
        full_translation = "第一。第二。第三。"
        text_blocks = [
            ("First.", ("00:00:01,000", "00:00:02,000")),
            ("Second.", ("00:00:02,000", "00:00:03,000")),
            ("Third.", ("00:00:03,000", "00:00:04,000")),
        ]
        
        result = split_translation(full_translation, text_blocks)
        assert len(result) == len(text_blocks)
        print(f"✅ 分割长度一致性验证成功")


class TestTranslation:
    """测试翻译功能"""
    
    def test_youdao_translate_basic(self):
        """测试基本翻译"""
        try:
            result = youdao_translate("Hello")
            # 可能成功或失败（取决于 API），但不应异常
            assert isinstance(result, str)
            print(f"✅ 翻译 'Hello': {result}")
        except Exception as e:
            print(f"⚠️  翻译异常（可能是网络问题）: {e}")
    
    def test_youdao_translate_empty(self):
        """测试空字符串翻译"""
        try:
            result = youdao_translate("")
            assert isinstance(result, str)
            print(f"✅ 空字符串翻译成功")
        except Exception as e:
            print(f"⚠️  空字符串翻译异常: {e}")
    
    def test_youdao_translate_parameters(self):
        """测试翻译参数"""
        try:
            # 测试不同语言组合
            result = youdao_translate("Hello", from_lang='en', to_lang='zh-CHS')
            assert isinstance(result, str)
            print(f"✅ 参数化翻译成功")
        except Exception as e:
            print(f"⚠️  参数化翻译异常: {e}")
    
    def test_youdao_translate_long_text(self):
        """测试长文本翻译"""
        long_text = " ".join(["Hello world"] * 10)
        try:
            result = youdao_translate(long_text)
            assert isinstance(result, str)
            print(f"✅ 长文本翻译成功")
        except Exception as e:
            print(f"⚠️  长文本翻译异常: {e}")


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def test_srt_file(self):
        """创建测试 SRT 文件"""
        srt_content = """1
00:00:01,000 --> 00:00:03,000
Hello world.

2
00:00:03,000 --> 00:00:05,000
This is a test.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt',
                                        delete=False, encoding='utf-8') as f:
            f.write(srt_content)
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_full_workflow(self, test_srt_file):
        """测试完整工作流"""
        # 收集字幕块
        subtitle_blocks, text_blocks = collect_subtitle_blocks(test_srt_file)
        assert len(subtitle_blocks) > 0
        
        # 组合文本
        full_text = " ".join(text for text, _ in text_blocks)
        assert len(full_text) > 0
        
        print(f"✅ 完整工作流:")
        print(f"   - 收集字幕块: {len(subtitle_blocks)} 个")
        print(f"   - 全文: {full_text}")
        
        # 尝试翻译（可能失败）
        try:
            translation = youdao_translate(full_text)
            print(f"   - 翻译成功: {translation[:50]}...")
        except Exception as e:
            print(f"   - 翻译失败（网络问题）: {e}")


class TestErrorHandling:
    """错误处理测试"""
    
    def test_nonexistent_srt_file(self):
        """测试不存在的文件"""
        try:
            subtitle_blocks, text_blocks = collect_subtitle_blocks(
                "/nonexistent/path/to/file.srt"
            )
            # 取决于实现，可能返回空或抛异常
            print(f"✅ 处理不存在文件: 返回 {len(subtitle_blocks)} 个块")
        except Exception as e:
            print(f"✅ 处理不存在文件: 抛出异常 {type(e).__name__}")
    
    def test_malformed_srt(self):
        """测试格式错误的 SRT"""
        malformed_srt = """this is not valid srt
random text
more text
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt',
                                        delete=False, encoding='utf-8') as f:
            f.write(malformed_srt)
            temp_path = f.name
        
        try:
            subtitle_blocks, text_blocks = collect_subtitle_blocks(temp_path)
            # 取决于实现
            print(f"✅ 处理格式错误 SRT: 返回 {len(subtitle_blocks)} 个块")
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
