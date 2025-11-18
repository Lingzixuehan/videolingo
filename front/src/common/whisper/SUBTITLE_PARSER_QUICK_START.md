# SubtitleParser 快速开始指南

## 概述

`SubtitleParser` 是一个强大的字幕解析模块，支持多种格式（SRT、ASS、SSA、SUB、VTT），可将字幕转换为统一的 JSON 结构。

## 支持的格式

- ✅ **SRT** (SubRip Subtitle Format)
- ✅ **ASS** (Advanced SubStation Alpha)
- ✅ **SSA** (SubStation Alpha)
- ✅ **SUB** (MicroDVD Subtitle Format)
- ✅ **VTT** (WebVTT Subtitle Format)

## 安装

确保已安装依赖：

```bash
pip install pysubs2
```

## 快速使用

### 方式 1: 导入模块

```python
from core.subtitle_parser import SubtitleParser

# 或者从顶层模块导入
from whisper import SubtitleParser
```

### 方式 2: 基本解析

```python
parser = SubtitleParser()

# 解析字幕文件
result = parser.parse_subtitle_file('video.srt')

# 访问解析结果
print(f"总句数: {result['total_sentences']}")
print(f"总时长: {result['duration']} 秒")
print(f"格式: {result['format']}")

# 遍历句子
for sentence in result['sentences']:
    print(f"{sentence['start']} - {sentence['end']}: {sentence['text']}")
```

## 三个核心用法

### 用法 1: 解析并返回字典

```python
result = parser.parse_subtitle_file('subtitle.srt')

# 返回结构
{
    'sentences': [
        {
            'index': 0,
            'start': 1.5,           # 开始时间（秒）
            'end': 4.2,             # 结束时间（秒）
            'text': 'Subtitle text', # 字幕文本
            'video_timestamp': '00:00:01,500 --> 00:00:04,200'
        },
        # ... 更多句子
    ],
    'total_sentences': 100,
    'duration': 3600.0,         # 总时长（秒）
    'source_file': 'subtitle.srt',
    'format': 'srt'
}
```

### 用法 2: 解析并保存为 JSON

```python
# 直接解析并保存为 JSON 文件
json_file = parser.parse_and_save_json('video.srt')

# 返回生成的 JSON 文件路径
# 例: 'video.json'
```

### 用法 3: 按时间查询句子

```python
result = parser.parse_subtitle_file('video.srt')

# 查询在特定时间的字幕
time_seconds = 30.5  # 30 秒 30 毫秒时的字幕
sentence = parser.get_sentence_at_time(result['sentences'], time_seconds)

if sentence:
    print(f"在 {time_seconds}s: {sentence['text']}")
else:
    print("该时刻无字幕")
```

## 实用示例

### 示例 1: 提取所有时间戳

```python
parser = SubtitleParser()
result = parser.parse_subtitle_file('video.srt')

for sentence in result['sentences']:
    print(f"{sentence['video_timestamp']}: {sentence['text']}")
```

### 示例 2: 统计字幕信息

```python
result = parser.parse_subtitle_file('video.srt')

print(f"总句数: {result['total_sentences']}")
print(f"总时长: {result['duration']} 秒")
print(f"平均句长: {result['duration'] / result['total_sentences']:.1f} 秒")

# 字幕密度（每分钟句数）
density = result['total_sentences'] / (result['duration'] / 60)
print(f"字幕密度: {density:.1f} 句/分钟")
```

### 示例 3: 过滤长字幕

```python
result = parser.parse_subtitle_file('video.srt')

# 找出超过 5 秒的字幕
long_subtitles = [
    s for s in result['sentences']
    if s['end'] - s['start'] > 5.0
]

print(f"找到 {len(long_subtitles)} 个长字幕")
```

### 示例 4: 与词汇提取结合

```python
from core.label import Labeler
from core.subtitle_parser import SubtitleParser

parser = SubtitleParser()
labeler = Labeler()

result = parser.parse_subtitle_file('video.srt')

# 对所有字幕进行词汇提取
for sentence in result['sentences']:
    text = sentence['text']
    # 使用 Labeler 提取单词及其定义
    labels = labeler.process_subtitle_file(text, sentence['index'])
```

### 示例 5: 格式转换

```python
# 将 ASS 格式转换为 SRT JSON
parser = SubtitleParser()

# 解析 ASS
result = parser.parse_subtitle_file('video.ass')

# 保存为 JSON（支持所有格式）
json_file = parser.parse_and_save_json('video.ass')
```

### 示例 6: 时间段查询

```python
parser = SubtitleParser()
result = parser.parse_subtitle_file('video.srt')

# 查找某个时间段内的所有字幕
start_time = 10.0  # 10 秒
end_time = 20.0    # 20 秒

segment_subtitles = [
    s for s in result['sentences']
    if s['start'] >= start_time and s['end'] <= end_time
]

for s in segment_subtitles:
    print(f"{s['start']:.1f}s: {s['text']}")
```

## 与其他模块集成

### 与 Labeler 集成

```python
from core.subtitle_parser import SubtitleParser
from core.label import Labeler

parser = SubtitleParser()
labeler = Labeler()

# 1. 解析字幕
result = parser.parse_subtitle_file('video.srt')

# 2. 逐句提取词汇
for sentence in result['sentences']:
    labels = labeler.process_subtitle_file(
        sentence['text'],
        sentence['index']
    )
```

### 与翻译模块集成

```python
from core.subtitle_parser import SubtitleParser
from core.translator import youdao_translate

parser = SubtitleParser()
result = parser.parse_subtitle_file('video.srt')

# 翻译每个句子
for sentence in result['sentences']:
    translation = youdao_translate(sentence['text'])
    print(f"原文: {sentence['text']}")
    print(f"翻译: {translation}")
```

### 与 GUI 集成

```python
# 在 GUI 中加载和显示字幕
from core.subtitle_parser import SubtitleParser

parser = SubtitleParser()
result = parser.parse_subtitle_file(subtitle_path)

# 在 GUI 中显示
for sentence in result['sentences']:
    add_to_listbox(
        f"[{sentence['start']:.1f}s] {sentence['text']}"
    )
```

## API 参考

### SubtitleParser 类

#### `parse_subtitle_file(file_path: str) -> dict`

解析字幕文件并返回结构化数据。

**参数:**
- `file_path` (str): 字幕文件路径

**返回:** dict - 包含句子列表和元数据的字典

**异常:**
- `FileNotFoundError`: 文件不存在
- `ValueError`: 不支持的文件格式

#### `parse_and_save_json(input_file: str, output_file: str = None) -> str`

解析字幕文件并保存为 JSON。

**参数:**
- `input_file` (str): 输入字幕文件路径
- `output_file` (str, optional): 输出 JSON 文件路径（默认为输入文件名 + .json）

**返回:** str - 生成的 JSON 文件路径

#### `get_sentence_at_time(sentences: list, time_seconds: float) -> dict | None`

在指定时间查询字幕。

**参数:**
- `sentences` (list): 句子列表（来自 parse_subtitle_file）
- `time_seconds` (float): 查询时间（秒）

**返回:** dict | None - 该时刻的句子或 None

## 常见问题

### Q: 支持中文字幕吗？
**A:** 是的，完全支持所有 UTF-8 编码的语言，包括中文、日文、阿拉伯语等。

### Q: 如果字幕文件有多行怎么办？
**A:** 多行字幕会被自动合并为单行，保留空格。

### Q: 如何处理样式标记（ASS/SSA）？
**A:** SubtitleParser 会自动移除所有样式标记（如 `{\c&HFFFFFF&}`），只保留纯文本。

### Q: 支持字幕编码问题吗？
**A:** pysubs2 会尝试自动检测编码。如有问题，建议转换为 UTF-8 编码。

### Q: 性能如何？
**A:** 能轻松处理 1000+ 句的大型字幕文件。

## 运行示例

查看 `examples/subtitle_parser_demo.py` 以了解更多实例：

```bash
python examples/subtitle_parser_demo.py
```

该脚本包含 6 个完整示例：
1. 基本解析
2. 解析并保存 JSON
3. 时间查询
4. 与 Labeler 集成
5. 与翻译模块集成
6. 完整工作流

## 文件输出

### JSON 输出格式

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

## 下一步

- 查看 `tests/test_subtitle_parser.py` 了解单元测试
- 查看 `README.md` 了解更多项目信息
- 查看 `USAGE_GUIDE.md` 了解完整使用说明
