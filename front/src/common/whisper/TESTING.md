# 🧪 Whisper 模块测试指南

## 概览

本项目包含两种类型的测试：

1. **快速测试** (`quick_test.py`) - 无需依赖，快速验证功能
2. **单元测试** (`tests/test_*.py`) - 使用 pytest 框架，完整的功能验证

## 快速测试

### 安装依赖

```bash
# 无需额外安装，使用项目现有依赖
pip install -r requirements.txt
```

### 运行快速测试

```bash
# 从 whisper 目录运行
python quick_test.py

# 输出示例：
# ======================================================================
#   🧪 Whisper 模块快速测试
# ======================================================================
# 
# 当前目录: D:\workspace\videolingo\front\src\common\whisper
# 
# ======================================================================
#   测试 1: StarDict 词典查询
# ======================================================================
# ✅ hello           -> 你好
# ✅ world           -> 世界
# ⚠️  python          -> 未找到
# ✅ code            -> 代码
```

### 快速测试包含的内容

| 编号 | 测试项 | 说明 |
|-----|--------|------|
| 1 | StarDict 词典查询 | 验证词典是否正常加载和查询 |
| 2 | 词汇难度分级 | 检查不同用户等级的词汇分类 |
| 3 | 单词查询 | 测试 Labeler 的单词查询功能 |
| 4 | 词汇标注器 | 处理 SRT 字幕并生成词汇标注 |
| 5 | 字幕解析 | 解析 SRT 格式字幕 |
| 6 | 翻译功能 | 测试有道翻译 API（需网络） |
| 7 | JSON 结构示例 | 显示输出 JSON 的完整结构 |

## 单元测试

### 安装 pytest

```bash
pip install pytest pytest-cov
```

### 运行单元测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_label.py -v
pytest tests/test_translator.py -v
pytest tests/test_stardict.py -v

# 运行特定测试
pytest tests/test_label.py::TestTokenization::test_simple_tokenize -v

# 运行包含特定关键字的测试
pytest -k "test_lookup" -v

# 显示详细输出
pytest tests/ -v -s

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

### 单元测试结构

#### 1. `test_label.py` - 词汇标注器测试

**测试类：**

- `TestTokenization` - 分词功能测试
  - `test_simple_tokenize()` - 简单分词
  - `test_tokenize_with_punctuation()` - 含标点分词
  - `test_tokenize_with_apostrophe()` - 含撇号分词
  - `test_tokenize_empty()` - 空字符串分词
  - `test_tokenize_numbers()` - 含数字分词

- `TestCandidateGeneration` - 候选词生成测试
  - `test_generate_lowercase()` - 生成小写候选
  - `test_generate_plural_removal()` - 移除复数
  - `test_generate_apostrophe_removal()` - 移除撇号
  - `test_generate_no_duplicates()` - 无重复验证

- `TestLabeler` - Labeler 类测试
  - `test_labeler_initialization()` - 初始化
  - `test_labeler_lookup()` - 单词查询
  - `test_labeler_lookup_nonexistent()` - 查询不存在词汇
  - `test_labeler_with_different_levels()` - 不同等级

- `TestSubtitleProcessing` - 字幕处理测试
  - `test_process_subtitle_file()` - 处理字幕
  - `test_output_structure()` - 输出结构验证
  - `test_word_map_structure()` - 词汇映射结构

- `TestVocabLevelIntegration` - 词汇等级集成测试
  - `test_different_user_levels()` - 不同用户等级

- `TestEdgeCases` - 边界情况测试
  - `test_empty_srt_file()` - 空 SRT 文件
  - `test_srt_with_special_characters()` - 特殊字符处理

#### 2. `test_translator.py` - 翻译模块测试

**测试类：**

- `TestHelperFunctions` - 辅助函数测试
  - `test_truncate()` - 字符串截断
  - `test_md5_encode()` - MD5 编码
  - `test_md5_consistent()` - MD5 一致性

- `TestSubtitleParsing` - 字幕解析测试
  - `test_collect_subtitle_blocks()` - 收集字幕块
  - `test_text_block_structure()` - 文本块结构
  - `test_parse_empty_srt()` - 解析空 SRT

- `TestSplitTranslation` - 翻译分割测试
  - `test_split_translation_basic()` - 基本分割
  - `test_split_translation_preserves_length()` - 长度保持

- `TestTranslation` - 翻译功能测试
  - `test_youdao_translate_basic()` - 基本翻译
  - `test_youdao_translate_empty()` - 空字符串翻译
  - `test_youdao_translate_parameters()` - 参数化翻译
  - `test_youdao_translate_long_text()` - 长文本翻译

- `TestIntegration` - 集成测试
  - `test_full_workflow()` - 完整工作流

- `TestErrorHandling` - 错误处理测试
  - `test_nonexistent_srt_file()` - 不存在文件
  - `test_malformed_srt()` - 格式错误 SRT

#### 3. `test_stardict.py` - 词典测试

**测试类：**

- `TestDictCsv` - 词典查询测试
  - `test_dict_initialization()` - 词典初始化
  - `test_query_existing_word()` - 查询存在词汇
  - `test_query_case_insensitive()` - 大小写不敏感
  - `test_query_nonexistent_word()` - 查询不存在词汇
  - `test_query_returns_dict()` - 返回结构验证
  - `test_query_result_content()` - 结果内容检查
  - `test_multiple_queries()` - 多词汇查询
  - `test_empty_query()` - 空查询
  - `test_special_characters()` - 特殊字符查询

- `TestDictCsvPerformance` - 性能测试
  - `test_query_performance()` - 查询性能基准

## 常见用例

### 场景 1: 快速验证所有功能

```bash
python quick_test.py
```

这会依次测试 7 个关键功能，约需 5-10 秒。

### 场景 2: 测试特定功能

```bash
# 只测试词汇标注器
pytest tests/test_label.py -v

# 只测试翻译模块
pytest tests/test_translator.py -v

# 只测试词典查询
pytest tests/test_stardict.py -v
```

### 场景 3: 调试单个测试

```bash
# 显示详细输出和打印语句
pytest tests/test_label.py::TestTokenization::test_simple_tokenize -v -s

# 输出示例：
# tests/test_label.py::TestTokenization::test_simple_tokenize
# ✅ 简单分词: Hello world this is Python -> ['Hello', 'world', 'this', 'is', 'Python']
# PASSED
```

### 场景 4: 生成覆盖率报告

```bash
pytest tests/ --cov=. --cov-report=html

# 在 htmlcov/index.html 中查看报告
```

### 场景 5: 忽略网络依赖

```bash
# 跳过需要网络的翻译测试
pytest tests/ -v -m "not skip_network"
```

## 测试文件创建指南

### 添加新的单元测试

1. 在 `tests/` 目录创建 `test_new_module.py`

```python
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from new_module import SomeClass

class TestSomeClass:
    def test_basic_functionality(self):
        """测试基本功能"""
        obj = SomeClass()
        assert obj is not None
        print(f"✅ 初始化成功")
    
    def test_another_function(self):
        """测试另一个函数"""
        result = obj.some_method()
        assert result is not None
        print(f"✅ 方法调用成功")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
```

2. 运行新测试

```bash
pytest tests/test_new_module.py -v
```

## 故障排除

### 问题 1: ModuleNotFoundError

**错误：** `ModuleNotFoundError: No module named 'whisper'`

**解决方案：**

```bash
# 确保在项目根目录运行
cd d:\workspace\videolingo\front\src\common\whisper

# 运行快速测试
python quick_test.py

# 或运行单元测试
pytest tests/ -v
```

### 问题 2: FileNotFoundError - 词典文件

**错误：** `FileNotFoundError: 未找到词典文件: data/ecdict.csv`

**解决方案：**

检查 `data/` 目录是否存在词典文件：

```bash
ls -la data/

# 应该看到：
# -rw-r--r--  ecdict.csv
# -rw-r--r--  ecdict.mini.csv
```

### 问题 3: 翻译 API 超时

**错误：** `ConnectionError` 或 `Timeout`

**解决方案：**

翻译功能需要网络连接。如果超时：

- 检查网络连接
- 跳过翻译测试：`pytest -k "not translate" -v`
- 增加超时时间（在代码中修改 timeout 参数）

### 问题 4: pytest 未安装

**错误：** `No module named 'pytest'`

**解决方案：**

```bash
pip install pytest pytest-cov
```

## 性能基准

在标准配置下的预期性能（参考值）：

| 操作 | 耗时 | 备注 |
|-----|------|------|
| 词典初始化 | ~200ms | 加载 CSV 到内存 |
| 单词查询 | 1-5ms | 依赖词典大小 |
| 分词 | <1ms | 100 字以内 |
| SRT 解析 | <10ms | 100 行以内 |
| 翻译 API 调用 | 500-2000ms | 依赖网络和文本长度 |

## 持续集成建议

### GitHub Actions 配置

创建 `.github/workflows/test.yml`：

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install pytest pytest-cov
        pip install -r requirements.txt
    
    - name: Run quick tests
      run: python quick_test.py
    
    - name: Run unit tests
      run: pytest tests/ -v --cov --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## 下一步

- 📖 查看 [README.md](README.md) 了解模块结构
- 💻 查看 [USAGE_GUIDE.md](USAGE_GUIDE.md) 了解使用示例
- 🚀 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 查看快速参考
