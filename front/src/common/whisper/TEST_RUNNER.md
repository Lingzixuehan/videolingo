# 📋 测试运行指南

## 快速开始 (30秒)

```bash
# 进入 whisper 目录
cd d:\workspace\videolingo\front\src\common\whisper

# 运行快速测试
python quick_test.py
```

**预期输出：**
- ✅ 所有测试通过！
- 耗时：5-15 秒（取决于网络连接，因为有翻译 API 调用）

---

## 测试类型对比

| 类型 | 文件 | 依赖 | 耗时 | 用途 |
|------|------|------|------|------|
| 快速测试 | `quick_test.py` | 无 (项目本身) | 5-15s | 快速验证所有功能 |
| 单元测试 | `tests/test_*.py` | pytest | 10-30s | 详细的功能验证 |
| 性能测试 | `tests/test_*.py` | pytest | 变动 | 性能基准测试 |

---

## 1️⃣ 快速测试 (推荐)

### 最简单的方式

```bash
python quick_test.py
```

### 输出解读

```
======================================================================
  🧪 Whisper 模块快速测试
======================================================================

当前目录: D:\workspace\videolingo\front\src\common\whisper

======================================================================
  测试 1: StarDict 词典查询
======================================================================
✅ hello           -> 你好
✅ world           -> 世界
...

======================================================================
  📊 测试总结
======================================================================

总测试数: 7
通过数: 7
失败数: 0
成功率: 100%

  ✅ 通过 - StarDict 词典查询
  ✅ 通过 - 词汇难度分级
  ✅ 通过 - 单词查询
  ✅ 通过 - 词汇标注器
  ✅ 通过 - 字幕解析
  ✅ 通过 - 翻译功能
  ✅ 通过 - JSON 结构示例

======================================================================
🎉 所有测试通过！
======================================================================
```

### 包含的 7 个测试

| # | 测试 | 检查内容 |
|---|------|--------|
| 1 | StarDict 词典查询 | 词典文件是否正常加载 |
| 2 | 词汇难度分级 | 不同用户等级的词汇分类逻辑 |
| 3 | 单词查询 | Labeler 单词查询功能 |
| 4 | 词汇标注器 | SRT 处理和词汇标注 |
| 5 | 字幕解析 | SRT 格式解析和提取 |
| 6 | 翻译功能 | 有道翻译 API（需网络） |
| 7 | JSON 结构示例 | 输出格式说明 |

---

## 2️⃣ 单元测试 (详细)

### 前置条件

```bash
# 安装 pytest
pip install pytest pytest-cov
```

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行特定测试文件

```bash
# 只测试词汇标注器
pytest tests/test_label.py -v

# 只测试翻译模块
pytest tests/test_translator.py -v

# 只测试词典
pytest tests/test_stardict.py -v
```

### 运行特定测试类

```bash
# 测试分词功能
pytest tests/test_label.py::TestTokenization -v

# 测试字幕解析
pytest tests/test_translator.py::TestSubtitleParsing -v
```

### 运行特定测试方法

```bash
pytest tests/test_label.py::TestTokenization::test_simple_tokenize -v
```

### 常用的 pytest 选项

```bash
# 显示打印输出
pytest tests/ -v -s

# 只运行包含 "translate" 的测试
pytest tests/ -k "translate" -v

# 生成 HTML 覆盖率报告
pytest tests/ --cov=. --cov-report=html

# 显示最慢的 10 个测试
pytest tests/ --durations=10

# 在首次失败时停止
pytest tests/ -x

# 显示本地变量
pytest tests/ -l

# 进入调试器 (pdb)
pytest tests/ --pdb
```

---

## 3️⃣ 常见问题排查

### 问题 1: 编码错误 (gbk codec)

**症状：** `UnicodeEncodeError: 'gbk' codec can't encode character...`

**解决：** 这是 Windows 控制台的编码问题，代码已自动处理，如果仍有问题：

```bash
# 方法 1: 使用 UTF-8 输出
chcp 65001

# 方法 2: 重定向到文件
python quick_test.py > test_output.txt
```

### 问题 2: 词典文件未找到

**症状：** `FileNotFoundError: 未找到词典文件`

**排查步骤：**

```bash
# 检查目录结构
ls -la data/

# 应该看到
# ecdict.csv
# ecdict.mini.csv
# lemma.en.txt
# ...

# 如果缺少文件，检查路径
python -c "import os; print(os.getcwd())"
```

### 问题 3: 翻译 API 超时

**症状：** `ConnectionError` 或 `Timeout`

**原因：** 网络问题或有道 API 不可用

**解决：**

```bash
# 方法 1: 检查网络
ping www.google.com

# 方法 2: 跳过翻译测试
pytest tests/ -k "not translate" -v

# 方法 3: 增加超时时间
# 修改 core/translator.py 中的 timeout 参数
```

### 问题 4: ModuleNotFoundError

**症状：** `ModuleNotFoundError: No module named 'whisper'` 或 `No module named 'pytest'`

**排查步骤：**

```bash
# 检查当前目录
cd d:\workspace\videolingo\front\src\common\whisper
pwd

# 安装 pytest
pip install pytest pytest-cov

# 检查 Python 路径
python -c "import sys; print(sys.path)"
```

### 问题 5: 导入错误

**症状：** `ImportError` 或 `relative import beyond top-level`

**解决：**

```bash
# 确保在正确的目录
cd d:\workspace\videolingo\front\src\common\whisper

# 测试导入
python -c "from whisper.core.label import Labeler; print('OK')"
```

---

## 4️⃣ 开发工作流

### 添加新的单元测试

```python
# 1. 创建 tests/test_new_feature.py
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from new_module import NewClass

class TestNewFeature:
    def test_basic(self):
        """测试基本功能"""
        obj = NewClass()
        assert obj is not None
        print(f"✅ 测试通过")

# 2. 运行新测试
pytest tests/test_new_feature.py -v

# 3. 整合到 quick_test.py（如果需要）
```

### 调试失败的测试

```bash
# 1. 显示详细输出和打印语句
pytest tests/test_label.py -v -s

# 2. 进入 Python 调试器
pytest tests/test_label.py --pdb

# 3. 在 test 前后打印状态
# 编辑 conftest.py 添加 fixtures
```

---

## 5️⃣ 性能基准

在标准配置下的典型性能（参考值）：

| 操作 | 耗时 | 说明 |
|-----|------|------|
| 词典初始化 | ~200ms | 加载 CSV 到内存 |
| 单词查询 | 1-5ms | 依赖词典大小 |
| SRT 解析 (100行) | <10ms | 快速 |
| 翻译 API 调用 | 500-2000ms | 依赖网络 |
| 词汇标注 (1000词) | ~500ms | 包括翻译 |
| GUI 启动 | ~2-3秒 | Tkinter 初始化 |

### 性能测试

```bash
# 运行性能测试
pytest tests/ -k "performance" -v

# 输出示例
# test_query_performance 通过
# ✅ 查询性能: 100 个查询耗时 0.523秒，平均 5.23ms
```

---

## 6️⃣ CI/CD 集成

### GitHub Actions 示例

创建 `.github/workflows/test.yml`：

```yaml
name: 测试

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 设置 Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: 安装依赖
      run: |
        pip install pytest pytest-cov
        pip install -r requirements.txt
    
    - name: 运行快速测试
      run: |
        cd videolingo\front\src\common\whisper
        python quick_test.py
    
    - name: 运行单元测试
      run: |
        cd videolingo\front\src\common\whisper
        pytest tests/ -v --cov --cov-report=xml
    
    - name: 上传覆盖率
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

### 本地 Git hooks

```bash
# 创建 pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
cd videolingo/front/src/common/whisper
python quick_test.py
if [ $? -ne 0 ]; then
    echo "❌ 测试失败，中止提交"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

---

## 7️⃣ 总结

| 场景 | 命令 | 耗时 |
|------|------|------|
| 快速验证 | `python quick_test.py` | 5-15s |
| 详细测试 | `pytest tests/ -v` | 10-30s |
| 覆盖率分析 | `pytest tests/ --cov --cov-report=html` | 20-40s |
| 调试单个测试 | `pytest tests/test_label.py::TestTokenization -v -s` | 变动 |
| 生产环境验证 | GitHub Actions (自动) | ~2-3min |

---

## 📚 相关文档

- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考卡片
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - 使用示例和工作流
- [README.md](README.md) - 模块概览
- [TESTING.md](TESTING.md) - 完整测试文档
