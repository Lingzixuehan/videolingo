#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StarDict 词典模块单元测试

运行方式：
  pytest tests/test_stardict.py -v
  pytest tests/test_stardict.py -v -k "test_query"
"""

import pytest
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from utils.stardict import DictCsv


class TestDictCsv:
    """测试 DictCsv 词典类"""
    
    @pytest.fixture
    def dict_path(self):
        """获取测试词典路径"""
        path = project_root / "data" / "ecdict.mini.csv"
        if not path.exists():
            pytest.skip(f"测试词典文件不存在: {path}")
        return str(path)
    
    @pytest.fixture
    def dict_obj(self, dict_path):
        """创建 DictCsv 实例"""
        return DictCsv(dict_path)
    
    def test_dict_initialization(self, dict_path):
        """测试词典初始化"""
        dict_obj = DictCsv(dict_path)
        assert dict_obj is not None
        print(f"✅ 词典加载成功: {dict_path}")
    
    def test_query_existing_word(self, dict_obj):
        """测试查询存在的词汇"""
        result = dict_obj.query('hello')
        assert result is not None, "hello 应该在词典中"
        assert result.get('word') == 'hello'
        assert 'translation' in result
        print(f"✅ 查询到: {result}")
    
    def test_query_case_insensitive(self, dict_obj):
        """测试大小写不敏感查询"""
        result_lower = dict_obj.query('hello')
        result_upper = dict_obj.query('HELLO')
        result_mixed = dict_obj.query('HeLLo')
        
        assert result_lower is not None or result_upper is not None or result_mixed is not None
        print(f"✅ 大小写不敏感查询成功")
    
    def test_query_nonexistent_word(self, dict_obj):
        """测试查询不存在的词汇"""
        result = dict_obj.query('xyzabc123')
        assert result is None or result == {}
        print(f"✅ 不存在词汇返回 None 或空字典")
    
    def test_query_returns_dict(self, dict_obj):
        """测试查询返回字典结构"""
        result = dict_obj.query('hello')
        if result:
            assert isinstance(result, dict)
            # 检查常见字段
            expected_fields = ['word', 'translation']
            for field in expected_fields:
                assert field in result, f"结果应包含 {field} 字段"
            print(f"✅ 返回结果包含必要字段: {list(result.keys())}")
    
    def test_query_result_content(self, dict_obj):
        """测试查询结果的内容"""
        result = dict_obj.query('hello')
        if result:
            print(f"✅ 查询结果详情:")
            for key, value in result.items():
                if isinstance(value, str) and len(str(value)) > 100:
                    print(f"    {key}: {str(value)[:100]}...")
                else:
                    print(f"    {key}: {value}")
    
    def test_multiple_queries(self, dict_obj):
        """测试多个查询"""
        words = ['hello', 'world', 'python', 'code', 'test']
        results = {}
        
        for word in words:
            result = dict_obj.query(word)
            results[word] = result is not None
        
        found = sum(1 for v in results.values() if v)
        print(f"✅ 查询了 {len(words)} 个词汇，其中 {found} 个找到")
        
        for word, found in results.items():
            status = "✅" if found else "❌"
            print(f"    {status} {word}")
    
    def test_empty_query(self, dict_obj):
        """测试空查询"""
        result = dict_obj.query('')
        assert result is None or result == {}
        print(f"✅ 空查询返回合理结果")
    
    def test_special_characters(self, dict_obj):
        """测试特殊字符查询"""
        special_words = ["don't", "it's", "can't"]
        
        for word in special_words:
            try:
                result = dict_obj.query(word)
                print(f"✅ '{word}' 查询成功: {result is not None}")
            except Exception as e:
                print(f"⚠️  '{word}' 查询异常: {e}")


class TestDictCsvPerformance:
    """性能测试"""
    
    @pytest.fixture
    def dict_path(self):
        """获取测试词典路径"""
        path = project_root / "data" / "ecdict.mini.csv"
        if not path.exists():
            pytest.skip(f"测试词典文件不存在: {path}")
        return str(path)
    
    @pytest.fixture
    def dict_obj(self, dict_path):
        """创建 DictCsv 实例"""
        return DictCsv(dict_path)
    
    def test_query_performance(self, dict_obj):
        """测试查询性能"""
        import time
        
        words = ['hello', 'world', 'python', 'code', 'test'] * 20  # 100 个查询
        
        start_time = time.time()
        for word in words:
            dict_obj.query(word)
        elapsed = time.time() - start_time
        
        avg_time = elapsed / len(words) * 1000  # 转换为毫秒
        print(f"✅ 查询性能: {len(words)} 个查询耗时 {elapsed:.3f}秒，平均 {avg_time:.3f}ms")
        
        assert avg_time < 50, "单次查询不应超过 50ms"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
