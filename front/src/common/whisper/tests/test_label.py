#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
词汇标注器 (Labeler) 模块单元测试

运行方式：
  pytest tests/test_label.py -v
  pytest tests/test_label.py -v -k "test_lookup"
"""

import pytest
import os
import sys
import json
import tempfile
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from core.label import Labeler, _tokenize, _generate_candidates
from utils.vocab_level import VocabLevel


class TestTokenization:
    """测试分词功能"""
    
    def test_simple_tokenize(self):
        """测试简单分词"""
        text = "Hello world this is Python"
        tokens = _tokenize(text)
        assert tokens == ['Hello', 'world', 'this', 'is', 'Python']
        print(f"✅ 简单分词: {text} -> {tokens}")
    
    def test_tokenize_with_punctuation(self):
        """测试含标点的分词"""
        text = "Hello, world! This is Python."
        tokens = _tokenize(text)
        assert len(tokens) > 0
        assert 'Hello' in tokens
        assert 'world' in tokens
        print(f"✅ 含标点分词: {text} -> {tokens}")
    
    def test_tokenize_with_apostrophe(self):
        """测试含撇号的分词"""
        text = "Don't worry, it's fine"
        tokens = _tokenize(text)
        assert "Don't" in tokens
        assert "it's" in tokens
        print(f"✅ 含撇号分词: {text} -> {tokens}")
    
    def test_tokenize_empty(self):
        """测试空字符串分词"""
        text = ""
        tokens = _tokenize(text)
        assert tokens == []
        print(f"✅ 空字符串分词成功")
    
    def test_tokenize_numbers(self):
        """测试含数字的分词"""
        text = "There are 123 people"
        tokens = _tokenize(text)
        assert "There" in tokens
        assert "are" in tokens
        print(f"✅ 含数字分词: {text} -> {tokens}")


class TestCandidateGeneration:
    """测试候选词生成"""
    
    def test_generate_lowercase(self):
        """测试生成小写候选"""
        candidates = _generate_candidates("HELLO")
        assert "hello" in candidates
        print(f"✅ 大写转小写: HELLO -> {candidates}")
    
    def test_generate_plural_removal(self):
        """测试移除复数 s"""
        candidates = _generate_candidates("words")
        assert "words" in candidates
        assert "word" in candidates
        print(f"✅ 复数移除: words -> {candidates}")
    
    def test_generate_apostrophe_removal(self):
        """测试移除撇号"""
        candidates = _generate_candidates("don't")
        assert "don't" in candidates
        assert "dont" in candidates
        print(f"✅ 撇号移除: don't -> {candidates}")
    
    def test_generate_no_duplicates(self):
        """测试候选词无重复"""
        candidates = _generate_candidates("Hello")
        assert len(candidates) == len(set(candidates))
        print(f"✅ 候选词无重复: {candidates}")


class TestLabeler:
    """测试 Labeler 类"""
    
    @pytest.fixture
    def dict_path(self):
        """获取测试词典路径"""
        path = project_root / "data" / "ecdict.mini.csv"
        if not path.exists():
            pytest.skip(f"测试词典文件不存在: {path}")
        return str(path)
    
    @pytest.fixture
    def labeler(self, dict_path):
        """创建 Labeler 实例"""
        return Labeler(dict_path, user_vocab_level='cet4')
    
    def test_labeler_initialization(self, dict_path):
        """测试 Labeler 初始化"""
        labeler = Labeler(dict_path)
        assert labeler is not None
        assert labeler._dict is not None
        print(f"✅ Labeler 初始化成功")
    
    def test_labeler_lookup(self, labeler):
        """测试单词查询"""
        result = labeler.lookup('hello')
        assert result is not None
        assert 'word' in result
        print(f"✅ 查询 'hello': {result}")
    
    def test_labeler_lookup_nonexistent(self, labeler):
        """测试查询不存在的词"""
        result = labeler.lookup('xyzabc123')
        # 返回 None 或空字典都可以
        assert result is None or result == {}
        print(f"✅ 查询不存在词汇返回合理结果")
    
    def test_labeler_with_different_levels(self, dict_path):
        """测试不同难度等级的 Labeler"""
        levels = ['basic', 'cet4', 'cet6', 'toefl']
        
        for level in levels:
            labeler = Labeler(dict_path, user_vocab_level=level)
            assert labeler.level_checker is not None
            print(f"✅ 初始化 {level.upper()} 等级 Labeler")


class TestSubtitleProcessing:
    """测试字幕处理"""
    
    @pytest.fixture
    def dict_path(self):
        """获取测试词典路径"""
        path = project_root / "data" / "ecdict.mini.csv"
        if not path.exists():
            pytest.skip(f"测试词典文件不存在: {path}")
        return str(path)
    
    @pytest.fixture
    def test_srt_file(self):
        """创建测试 SRT 文件"""
        srt_content = """1
00:00:01,000 --> 00:00:03,000
Hello world, this is a test.

2
00:00:03,000 --> 00:00:05,000
Python is great for programming.

3
00:00:05,000 --> 00:00:07,000
Let's learn together.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', 
                                        delete=False, encoding='utf-8') as f:
            f.write(srt_content)
            temp_path = f.name
        
        yield temp_path
        
        # 清理
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_process_subtitle_file(self, dict_path, test_srt_file):
        """测试处理字幕文件"""
        labeler = Labeler(dict_path, user_vocab_level='cet4')
        result = labeler.process_subtitle_file(test_srt_file)
        
        assert result is not None
        assert 'source' in result
        assert 'blocks' in result
        assert 'word_map' in result
        
        print(f"✅ 处理字幕文件成功")
        print(f"   - 字幕块数: {len(result['blocks'])}")
        print(f"   - 词汇数: {len(result['word_map'])}")
    
    def test_output_structure(self, dict_path, test_srt_file):
        """测试输出结构"""
        labeler = Labeler(dict_path, user_vocab_level='cet4')
        result = labeler.process_subtitle_file(test_srt_file)
        
        # 检查顶层结构
        assert isinstance(result, dict)
        required_keys = ['source', 'path', 'blocks', 'word_map']
        for key in required_keys:
            assert key in result, f"缺少必要字段: {key}"
        
        # 检查 blocks 结构
        if result['blocks']:
            block = result['blocks'][0]
            assert 'index' in block
            assert 'start' in block
            assert 'end' in block
            assert 'text' in block
        
        print(f"✅ 输出结构验证成功")
    
    def test_word_map_structure(self, dict_path, test_srt_file):
        """测试词汇映射结构"""
        labeler = Labeler(dict_path, user_vocab_level='cet4')
        result = labeler.process_subtitle_file(test_srt_file)
        
        if result['word_map']:
            word = list(result['word_map'].keys())[0]
            word_info = result['word_map'][word]
            
            # 检查词汇信息结构
            assert 'entry' in word_info
            assert 'is_new' in word_info
            assert 'difficulty' in word_info
            
            print(f"✅ 词汇映射结构验证成功")
            print(f"   示例词汇: {word}")
            print(f"   - 翻译: {word_info['entry'].get('translation', 'N/A')}")
            print(f"   - 新词: {word_info['is_new']}")
            print(f"   - 难度: {word_info['difficulty']}")


class TestVocabLevelIntegration:
    """词汇等级集成测试"""
    
    @pytest.fixture
    def dict_path(self):
        """获取测试词典路径"""
        path = project_root / "data" / "ecdict.mini.csv"
        if not path.exists():
            pytest.skip(f"测试词典文件不存在: {path}")
        return str(path)
    
    def test_different_user_levels(self, dict_path):
        """测试不同用户等级的标注结果"""
        srt_content = """1
00:00:01,000 --> 00:00:03,000
Hello world, welcome to Python.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', 
                                        delete=False, encoding='utf-8') as f:
            f.write(srt_content)
            temp_path = f.name
        
        try:
            levels = ['basic', 'cet4', 'cet6', 'toefl']
            
            for level in levels:
                labeler = Labeler(dict_path, user_vocab_level=level)
                result = labeler.process_subtitle_file(temp_path)
                
                new_words = len(result.get('new_words', []))
                print(f"✅ {level.upper():10} 等级: {new_words} 个新词")
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestEdgeCases:
    """边界情况测试"""
    
    @pytest.fixture
    def dict_path(self):
        """获取测试词典路径"""
        path = project_root / "data" / "ecdict.mini.csv"
        if not path.exists():
            pytest.skip(f"测试词典文件不存在: {path}")
        return str(path)
    
    def test_empty_srt_file(self, dict_path):
        """测试空 SRT 文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', 
                                        delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = f.name
        
        try:
            labeler = Labeler(dict_path)
            result = labeler.process_subtitle_file(temp_path)
            assert result is not None
            print(f"✅ 处理空 SRT 文件成功")
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_srt_with_special_characters(self, dict_path):
        """测试含特殊字符的 SRT"""
        srt_content = """1
00:00:01,000 --> 00:00:03,000
Hello! @#$%^&* Don't worry.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', 
                                        delete=False, encoding='utf-8') as f:
            f.write(srt_content)
            temp_path = f.name
        
        try:
            labeler = Labeler(dict_path)
            result = labeler.process_subtitle_file(temp_path)
            assert result is not None
            print(f"✅ 处理含特殊字符 SRT 成功")
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
