# Videolingo Whisper 模块

一体化字幕处理模块，集成 **字幕提取**、**字幕嵌入**、字幕解析、翻译、词汇标注等功能。

**✅ 核心功能（生产就绪）：**
- 🎬 **字幕提取** - 使用 Whisper 从视频提取字幕 (GPU 加速)
- 🎞️ **字幕嵌入** - 使用 FFmpeg 将字幕嵌入视频
- 📝 **字幕解析** - 支持多种格式 (SRT, ASS, VTT 等)
- 📚 **词汇标注** - 自动提取和标注词汇信息
- 🌐 **字幕翻译** - 有道翻译 API 集成

## 目录结构

```
whisper/
├── README.md                     # 本文档
├── __init__.py                   # 包初始化
├── core/                         # 核心功能模块
│   ├── __init__.py
│   ├── subtitle_extractor.py     # 字幕提取 (NEW - 核心功能)
│   ├── subtitle_embedder.py      # 字幕嵌入 (NEW - 核心功能)
│   ├── subtitle_parser.py        # 字幕解析
│   ├── label.py                  # 词汇标注
│   ├── translator.py             # 翻译模块
│   └── video_workflow.py         # 完整工作流
├── utils/                        # 工具模块
│   ├── __init__.py
│   ├── dict_utils.py             # 字典工具函数
│   ├── linguist.py               # 语言学处理工具
│   ├── vocab_level.py            # 词汇等级评估
│   ├── stardict.py               # StarDict 词典解析
│   └── del_bfz.py                # 辅助处理工具
├── data/                         # 词典数据文件
│   ├── ecdict.csv                # 完整词典（CSV 格式）
│   ├── ecdict.mini.csv           # 精简词典
│   ├── lemma.en.txt              # 英文词根数据
│   ├── resemble.txt              # 相似词数据
│   ├── wordroot.txt              # 词根数据
│   └── LICENSE                   # 数据许可证
├── gui/                          # GUI 应用
│   ├── __init__.py
│   └── whisper.py                # Tkinter GUI 应用
├── examples/                     # 示例代码
│   ├── input.mp4                 # 测试视频
│   ├── test_integration.py       # 集成测试 (NEW)
│   ├── test_whisper_simple.py    # 简单提取测试
│   ├── test_video_workflow.py    # 完整工作流演示
│   ├── subtitle_parser_demo.py   # 字幕解析示例
│   └── test_output/              # 测试输出文件夹
│       ├── input.srt             # 提取的字幕
│       ├── input.json            # JSON 格式字幕
│       └── input-labels.json     # 词汇标注
├── tests/                        # 单元测试
│   ├── __init__.py
│   ├── test_label.py
│   ├── test_translator.py
│   ├── test_subtitle_parser.py
│   └── ...
└── QUICK_REFERENCE.md            # 快速参考
```

## 快速开始

### 1. 字幕提取（核心功能）

从视频提取字幕，自动生成 SRT 文件：

```python
from whisper.core.subtitle_extractor import SubtitleExtractor

# 创建提取器
extractor = SubtitleExtractor(model='base')

# 提取字幕
result = extractor.extract(
    video_path='input.mp4',
    output_dir='./output',
    progress_callback=lambda msg: print(msg)
)

# 获取结果
print(f"SRT 文件: {result['srt_path']}")
print(f"JSON 文件: {result['json_path']}")
```

**特性：**
- ✅ GPU 加速支持 (CUDA)
- ✅ 自动生成 SRT 和 JSON 格式
- ✅ 实时进度反馈
- ✅ 支持多种语言

### 2. 字幕嵌入（核心功能）

将字幕嵌入到视频中：

```python
from whisper.core.subtitle_embedder import SubtitleEmbedder

# 创建嵌入器
embedder = SubtitleEmbedder()

# 嵌入字幕
output_video = embedder.embed(
    video_path='input.mp4',
    subtitle_path='input.srt',
    output_path='output_with_subs.mp4'
)

print(f"输出视频: {output_video}")
```

**特性：**
- ✅ 支持 SRT、ASS 等格式
- ✅ 自定义字幕样式
- ✅ 自动路径处理
- ✅ FFmpeg 优化

### 3. 完整工作流

提取字幕 -> 嵌入视频 -> 标注词汇：

```python
from whisper.core.subtitle_extractor import SubtitleExtractor
from whisper.core.subtitle_embedder import SubtitleEmbedder
from whisper.core.label import Labeler

# 步骤 1: 提取字幕
extractor = SubtitleExtractor(model='base')
result = extractor.extract('input.mp4', './output')
srt_path = result['srt_path']

# 步骤 2: 嵌入字幕
embedder = SubtitleEmbedder()
output_video = embedder.embed('input.mp4', srt_path)

# 步骤 3: 标注词汇
labeler = Labeler()
labels = labeler.process_subtitle_file(srt_path)
print(f"提取词汇数: {len(labels['word_map'])}")
```

## 模块功能说明

### 核心功能 (core/)

#### `subtitle_extractor.py` - 字幕提取 (✅ 生产就绪)

使用 Whisper 从视频提取字幕，自动生成 SRT 和 JSON 文件。

```python
from whisper.core.subtitle_extractor import SubtitleExtractor, extract_subtitles_from_video

# 方式 1: 类方法
extractor = SubtitleExtractor(model='base')
result = extractor.extract_with_gpu_check(
    video_path='video.mp4',
    output_dir='./output',
    progress_callback=print
)

# 方式 2: 便捷函数
srt_path = extract_subtitles_from_video('video.mp4', model='base')
```

**输出文件：**
- `video.srt` - SRT 格式字幕 (标准格式)
- `video.json` - JSON 格式字幕 (便于处理)

**关键方法：**
- `extract()` - 基础提取
- `extract_with_gpu_check()` - 提取并显示 GPU 信息
- `_check_dependencies()` - 检查依赖

#### `subtitle_embedder.py` - 字幕嵌入 (✅ 生产就绪)

使用 FFmpeg 将字幕嵌入到视频。

```python
from whisper.core.subtitle_embedder import SubtitleEmbedder, embed_subtitles

# 方式 1: 类方法
embedder = SubtitleEmbedder()
output = embedder.embed(
    video_path='input.mp4',
    subtitle_path='input.srt',
    output_path='output_with_subs.mp4'
)

# 方式 2: 便捷函数
output = embed_subtitles('input.mp4', 'input.srt')
```

**输出文件：**
- `video_with_subs.mp4` - 嵌入字幕的视频

**高级功能：**
- 自定义字幕样式 (字体、大小、颜色)
- 自动路径处理 (Windows/Linux)
- 调试日志输出

#### `subtitle_parser.py` - 字幕解析

多格式字幕解析器，支持 SRT、ASS、SSA、SUB、VTT 等格式。

```python
from whisper import SubtitleParser

parser = SubtitleParser()

# 解析任意格式的字幕
result = parser.parse_subtitle_file('video.srt')

# 访问结果
for sentence in result['sentences']:
    print(f"{sentence['start']}s: {sentence['text']}")

# 保存为 JSON
json_file = parser.parse_and_save_json('video.srt')

# 按时间查询
subtitle = parser.get_sentence_at_time(result['sentences'], 30.5)
```

**支持格式：** SRT, ASS, SSA, SUB, VTT

**输出格式：**
```json
{
  "sentences": [
    {
      "index": 0,
      "start": 1.5,
      "end": 4.2,
      "text": "字幕文本",
      "video_timestamp": "00:00:01,500 --> 00:00:04,200"
    }
  ],
  "total_sentences": 100,
  "duration": 3600.0,
  "source_file": "video.srt",
  "format": "srt"
}
```

**主要特性：**
- 支持多种字幕格式
- 自动移除 ASS/SSA 样式标记
- 精确时间转换（毫秒级）
- 支持按时间查询字幕
- 直接导出为 JSON

#### `label.py` - 词汇标注
```python
from whisper.core.label import Labeler

# 初始化标注器
labeler = Labeler()

# 处理 SRT 字幕文件
result = labeler.process_subtitle_file('subtitle.srt')
# 输出：
# - subtitle-labels.json：包含每个单词的词典信息和词性等
# - subtitle_blocks：字幕块信息
# - word_map：全局词汇映射表
```

**功能：**
- 解析 SRT/ASS 字幕文件
- 对每个单词进行查词
- 生成 JSON 格式的词汇标签文件
- 支持词形变换（复数、过去式、撇号等）

**输出格式：**
```json
{
  "source": "subtitle.srt",
  "path": "/path/to/subtitle.srt",
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
            "definition": "...",
            "pos": "int"
          }
        }
      ]
    }
  ],
  "word_map": { /* 去重的全局词汇 */ }
}
```

#### `translator.py` - 翻译
```python
from whisper.core.translator import youdao_translate

# 翻译单条文本
result = youdao_translate("Hello world", from_lang='en', to_lang='zh-CHS')
# 输出: "你好世界"

# 处理 SRT 字幕并生成中文/双语版本
from whisper.core.translator import collect_subtitle_blocks, split_translation

subtitle_blocks, text_blocks = collect_subtitle_blocks('input.srt')
full_text = ' '.join(text for text, _ in text_blocks)
zh_translation = youdao_translate(full_text, from_lang='en', to_lang='zh-CHS')
zh_segments = split_translation(zh_translation, text_blocks)
```

**功能：**
- 调用有道翻译 API
- 批量翻译字幕文本
- 按原文长度比例分配翻译文本
- 生成中文 SRT (`-zh.srt`) 和双语 SRT (`-bi.srt`)

### 工具模块 (utils/)

#### `dict_utils.py` - 字典工具
提供字典操作的辅助函数

#### `stardict.py` - StarDict 词典解析
```python
from whisper.utils.stardict import DictCsv

# 加载 CSV 格式词典
dict_csv = DictCsv('data/ecdict.csv')

# 查询单词
entry = dict_csv.query('hello')
# 返回: {'word': 'hello', 'phonetic': '...', 'translation': '...', ...}
```

#### `vocab_level.py` - 词汇等级
评估单词的难度等级（如 CET-4、CET-6、TOEFL 等）

#### `linguist.py` - 语言学工具
- 词形变换（名词复数、动词时态等）
- 词根提取
- 语言学分析

### 数据模块 (data/)

| 文件 | 大小 | 说明 |
|-----|------|------|
| `ecdict.csv` | ~63 MB | 完整英汉词典（20 万+ 词条） |
| `ecdict.mini.csv` | ~4 KB | 精简版词典 |
| `lemma.en.txt` | ~2.3 MB | 英文词根数据库 |
| `resemble.txt` | ~500 KB | 相似词数据 |
| `wordroot.txt` | ~385 KB | 词根文件 |

### GUI 应用 (gui/)

```python
# 运行 GUI 应用
python -m whisper.gui.whisper
```

**功能：**
- 选择视频文件
- 选择 Whisper 模型（tiny/base/small/medium/large）
- 一键提取字幕并嵌入视频
- 导入本地字幕进行翻译和词汇标注

## 环境依赖

### 基础依赖
- Python 3.11+
- ffmpeg
- OpenAI Whisper
- PyTorch

### 详细安装步骤

#### 1. 安装 PyTorch

```bash
# CPU 版本（快速安装）
pip install torch torchvision torchaudio

# GPU版本（以cuda12.4为例）
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 -f https://mirrors.aliyun.com/pytorch-wheels/cu124
```

#### 2. 安装 FFmpeg
先在ffmpeg官网下载：https://ffmpeg.org/

```bash
pip install ffmpeg-python
```

#### 3. 安装 Whisper 和其他依赖

```bash
pip install -U openai-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
```

#### 4. 验证安装

```bash
python -c "from core.subtitle_extractor import SubtitleExtractor; print('✅ 提取器已安装')"
python -c "from core.subtitle_embedder import SubtitleEmbedder; print('✅ 嵌入器已安装')"
```

## 测试说明

### 集成测试（推荐）

测试完整的提取和嵌入工作流：

```bash
cd examples
python test_integration.py
```

**测试输出：**
```
✅ 字幕提取成功!
   SRT 文件: examples/test_output/input.srt
   处理时间: 6.56 秒

✅ 字幕嵌入成功!
   输出视频: examples/input_with_subs.mp4
   处理时间: 2.35 秒

✅ 所有测试完成!
```

### 简单提取测试

只测试字幕提取功能：

```bash
cd examples
python test_whisper_simple.py
```

### 完整工作流测试

包含解析、嵌入、词汇标注的完整测试：

```bash
cd examples
python test_video_workflow.py
```

## 测试结果

### 文件提取测试 (2025-11-18)

**测试视频:** `input.mp4` (5.02 MB, 33.2 秒)

**提取结果：**
```
✅ 字幕提取: 4 段落，588 字节
✅ JSON 格式: 2504 字节
✅ 词汇标注: 52 个词汇提取
✅ 字幕嵌入: 4.24 MB 输出视频

处理时间:
  - 提取: 6.56 秒
  - 嵌入: 2.35 秒
  - 总计: 8.91 秒

处理速度: 1.4 MB/s (GPU 加速)
```

**提取的字幕样本：**
```
1
00:00:00,000 --> 00:00:08,000
Yes, I came here. I think about five years ago I was 16 and just about to release my first

2
00:00:08,000 --> 00:00:17,600
single Tim McGraw and so we were traveling up the West Coast in a rental car and I was doing

3
00:00:17,600 --> 00:00:21,760
my homework in the backseat. I was like homeschooled in 10th grade and it's wonderful to be back

4
00:00:21,760 --> 00:00:28,199
here and have so many of you come out this time around. It's amazing. Yes, I came here.
```

## 使用示例

### 1. 字幕提取完整示例

```python
from whisper.core.subtitle_extractor import SubtitleExtractor

# 创建提取器实例
extractor = SubtitleExtractor(model='base')

# 定义进度回调
def on_progress(message):
    print(f"[提取] {message}")

# 执行提取
result = extractor.extract_with_gpu_check(
    video_path='video.mp4',
    output_dir='./subtitles',
    progress_callback=on_progress
)

# 使用结果
if result['success']:
    print(f"✅ SRT 文件: {result['srt_path']}")
    print(f"✅ JSON 文件: {result['json_path']}")
```

### 2. 字幕嵌入完整示例

```python
from whisper.core.subtitle_embedder import SubtitleEmbedder

embedder = SubtitleEmbedder()

# 标准嵌入
output = embedder.embed(
    video_path='input.mp4',
    subtitle_path='subtitles.srt',
    output_path='output.mp4'
)

# 自定义样式嵌入
output = embedder.embed_with_custom_style(
    video_path='input.mp4',
    subtitle_path='subtitles.srt',
    font_name='Arial',
    font_size=28,
    primary_color='&H00FFFFFF',  # 白色
    outline_color='&H00000000'   # 黑色
)

print(f"输出视频: {output}")
```

### 3. 词汇标注

```python
from whisper.core.label import Labeler

labeler = Labeler(dict_csv_path='whisper/data/ecdict.csv')
result = labeler.process_subtitle_file('subtitle.srt')

print(f"处理了 {len(result['blocks'])} 个字幕块")
print(f"共 {len(result['word_map'])} 个单词")
```

### 字幕翻译

```python
from whisper.core.translator import youdao_translate, collect_subtitle_blocks, split_translation

# 收集字幕块
subtitle_blocks, text_blocks = collect_subtitle_blocks('input.srt')

# 翻译整体文本
full_text = ' '.join(text for text, _ in text_blocks)
zh_translation = youdao_translate(full_text, from_lang='en', to_lang='zh-CHS')

# 分割翻译结果
zh_segments = split_translation(zh_translation, text_blocks)

# 生成输出文件
```

### GUI 应用

```bash
python -m whisper.gui.whisper
```

## 常见问题

**Q: 如何修改翻译 API Key？**
A: 编辑 `core/translator.py`，修改 `YOUDAO_APP_KEY` 和 `YOUDAO_APP_SECRET`

**Q: 词汇等级如何评估？**
A: 使用 `utils/vocab_level.py` 的评估函数

**Q: 如何自定义词典？**
A: 将自定义词典放在 `data/` 目录，修改 `core/label.py` 的加载逻辑

## 相关链接

- Whisper 官方：https://github.com/openai/whisper
- PyTorch 官方：https://pytorch.org/
- CUDA 工具包：https://developer.nvidia.com/cuda-toolkit
- 有道翻译 API：https://ai.youdao.com/