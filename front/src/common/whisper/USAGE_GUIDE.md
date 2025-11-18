# Whisper 模块使用指南

本指南详细说明如何使用 whisper 模块的各项功能。

## 快速开始

### 安装依赖

```bash
# 激活虚拟环境
conda activate whisper-env

# 安装必要的包
pip install requests ffmpeg-python
```

### 导入模块

```python
# 方式 1：直接导入主要功能
from whisper import Labeler, youdao_translate

# 方式 2：导入具体模块
from whisper.core.label import Labeler
from whisper.core.translator import youdao_translate, collect_subtitle_blocks, split_translation
from whisper.utils.stardict import DictCsv
from whisper.utils.vocab_level import VocabLevelChecker, VocabLevel
```

---

## 功能 1：词汇标注

### 基本用法

```python
from whisper.core.label import Labeler

# 初始化标注器（自动加载 ecdict.csv）
labeler = Labeler()

# 处理 SRT 字幕文件
result = labeler.process_subtitle_file('path/to/subtitle.srt')

# 查看处理结果
print(f"字幕块数：{len(result['blocks'])}")
print(f"词汇总数：{len(result['word_map'])}")
print(f"输出文件：{result['path']}-labels.json")
```

### 指定输出路径

```python
# 指定自定义词典文件
labeler = Labeler(dict_csv_path='custom/path/ecdict.csv')

# 指定输出 JSON 文件路径
result = labeler.process_subtitle_file(
    subtitle_path='input.srt',
    out_json='output/labels.json'
)
```

### 设置词汇难度等级

```python
# 支持的等级：'basic', 'cet4', 'cet6', 'toefl', 'ielts', 'gre', 'advanced'
labeler = Labeler(user_vocab_level='cet6')

result = labeler.process_subtitle_file('subtitle.srt')
```

### 查询单个单词

```python
# 查询单词的详细信息
entry = labeler.lookup('hello')
print(entry)
# 输出：
# {
#     'word': 'hello',
#     'phonetic': 'həˈləʊ',
#     'definition': 'used as a greeting',
#     'translation': '你好',
#     'pos': 'int',
#     'collins': '...',
#     'oxford': '...',
#     'tag': '...',
#     ...
# }
```

### 输出 JSON 结构

```json
{
  "source": "subtitle.srt",
  "path": "/absolute/path/to/subtitle.srt",
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
            "definition": "used as a greeting",
            "pos": "int"
          }
        }
      ]
    }
  ],
  "word_map": {
    "hello": { /* entry */ },
    "world": { /* entry */ }
  }
}
```

---

## 功能 2：字幕翻译

### 翻译单条文本

```python
from whisper.core.translator import youdao_translate

# 翻译单句
result = youdao_translate('Hello world', from_lang='en', to_lang='zh-CHS')
print(result)  # 输出：你好世界
```

### 批量翻译字幕

```python
from whisper.core.translator import (
    collect_subtitle_blocks,
    youdao_translate,
    split_translation
)

# 1. 收集字幕块信息
subtitle_blocks, text_blocks = collect_subtitle_blocks('input.srt')

# subtitle_blocks: 包含序号和时间戳
# text_blocks: [(文本1, 长度1), (文本2, 长度2), ...]

# 2. 合并所有文本进行翻译
full_text = ' '.join(text for text, _ in text_blocks)
print(f"总文本长度：{len(full_text)} 字符")

# 3. 调用翻译接口
zh_translation = youdao_translate(
    full_text, 
    from_lang='en', 
    to_lang='zh-CHS'
)

# 4. 按原文长度比例分配翻译
zh_segments = split_translation(zh_translation, text_blocks)

# 5. 生成中文和双语字幕
with open('output-zh.srt', 'w', encoding='utf-8') as zh_file, \
     open('output-bi.srt', 'w', encoding='utf-8') as bi_file:
    
    for i, (subtitle_block, (en_text, _)) in enumerate(zip(subtitle_blocks, text_blocks)):
        zh_text = zh_segments[i]
        
        # 写入中文字幕
        for line in subtitle_block:  # 序号 + 时间戳
            zh_file.write(line)
        zh_file.write(zh_text + '\n\n')
        
        # 写入双语字幕
        for line in subtitle_block:
            bi_file.write(line)
        bi_file.write(en_text + '\n')
        bi_file.write(zh_text + '\n\n')

print("✓ 生成中文字幕：output-zh.srt")
print("✓ 生成双语字幕：output-bi.srt")
```

### 翻译支持的语言

- `from_lang`: 源语言，如 `'en'` (English)
- `to_lang`: 目标语言
  - `'zh-CHS'`: 简体中文
  - `'zh-CHT'`: 繁体中文
  - `'ja'`: 日语
  - `'ko'`: 韩语
  - 其他语言代码请参考有道翻译 API 文档

---

## 功能 3：词汇难度评估

### 检查单词难度

```python
from whisper.utils.vocab_level import VocabLevelChecker, VocabLevel

# 初始化检查器（设定用户词汇等级为 CET-6）
checker = VocabLevelChecker(VocabLevel.CET6)

# 检查单词是否在用户词汇等级内
is_known = checker.is_word_in_level('hello')  # True
is_unknown = checker.is_word_in_level('serendipity')  # False (GRE 级别)
```

### 词汇等级体系

| 等级 | 类型 | 示例 |
|-----|------|------|
| BASIC | 基础词汇 | ~1000 词 |
| CET4 | 大学四级 | ~4500 词 |
| CET6 | 大学六级 | ~6000 词 |
| TOEFL | 托福 | ~8000 词 |
| IELTS | 雅思 | ~8000 词 |
| GRE | 研究生入学 | ~12000 词 |
| ADVANCED | 高级 | 全部词汇 |

---

## 功能 4：字典查询

### 直接查询 CSV 词典

```python
from whisper.utils.stardict import DictCsv

# 加载词典
dict_csv = DictCsv('whisper/data/ecdict.csv')

# 查询单词
entry = dict_csv.query('hello')
print(entry)
# {'word': 'hello', 'phonetic': '...', 'translation': '...', ...}

# 查询不存在的单词返回 None
entry = dict_csv.query('xyzabc')
print(entry)  # None
```

### 支持的字典文件

| 文件 | 大小 | 词条数 | 说明 |
|-----|------|--------|------|
| `ecdict.csv` | 63 MB | 20 万+ | 完整词典（推荐） |
| `ecdict.mini.csv` | 4 KB | ~1000 | 精简版，仅示例 |

---

## 功能 5：使用 GUI 应用

### 启动 GUI

```bash
# 方法 1：直接运行
python -m whisper.gui.whisper

# 方法 2：在虚拟环境中运行
conda activate whisper-env
python -m whisper.gui.whisper
```

### GUI 功能

1. **选择视频文件**
   - 点击 "..." 按钮选择视频文件
   - 支持格式：mp4, avi, mkv, mov, wmv

2. **选择 Whisper 模型**
   - tiny: 最快（但准确度低）
   - base: 推荐用于演示
   - small: 较好的平衡
   - medium: 高准确度
   - large: 最高准确度（最慢）

3. **提取字幕**
   - 点击 "提取并嵌入字幕"
   - 自动进行：Whisper 提取 → 词汇标注 → 翻译 → 嵌入
   - 生成文件：
     - `video-zh.srt`: 中文字幕
     - `video-bi.srt`: 双语字幕
     - `video_with_subs.mp4`: 嵌入字幕的视频

4. **导入本地字幕**
   - 点击 "导入本地字幕"
   - 对已有字幕进行：词汇标注 → 翻译 → 嵌入
   - 支持格式：srt, ass

---

## 功能 6：字幕嵌入

### 使用 FFmpeg 嵌入

```python
from whisper.gui.whisper import embed_subtitles

# 嵌入字幕到视频
output_video = embed_subtitles(
    video_path='input.mp4',
    subtitle_path='subtitle.srt'
)

if output_video:
    print(f"✓ 成功：{output_video}")
else:
    print("✗ 失败，请检查 FFmpeg 是否正确安装")
```

### 字幕格式要求

- 格式：SRT (SubRip)
- 编码：UTF-8
- 结构：
  ```
  1
  00:00:01,000 --> 00:00:03,000
  Hello world
  
  2
  00:00:03,500 --> 00:00:05,000
  Welcome to Videolingo
  ```

---

## 完整工作流示例

### 示例 1：从视频提取字幕到词汇学习

```python
from whisper.core.label import Labeler
from whisper.core.translator import youdao_translate, collect_subtitle_blocks, split_translation
import subprocess
import sys

def process_video_complete(video_path, model='base', output_dir='./output'):
    """完整的视频处理流程"""
    
    # 1. 使用 Whisper 提取字幕
    print("📝 步骤 1：提取字幕...")
    srt_path = f"{output_dir}/subtitle.srt"
    cmd = [
        sys.executable, '-m', 'whisper',
        video_path,
        '--model', model,
        '--language', 'English',
        '--task', 'translate',
        '--output_format', 'srt',
        '--output_dir', output_dir
    ]
    subprocess.run(cmd)
    
    # 2. 词汇标注
    print("🔤 步骤 2：词汇标注...")
    labeler = Labeler()
    result = labeler.process_subtitle_file(srt_path)
    print(f"   ✓ 处理 {len(result['blocks'])} 个字幕块")
    print(f"   ✓ 提取 {len(result['word_map'])} 个单词")
    
    # 3. 翻译
    print("🌐 步骤 3：翻译字幕...")
    subtitle_blocks, text_blocks = collect_subtitle_blocks(srt_path)
    full_text = ' '.join(text for text, _ in text_blocks)
    zh_translation = youdao_translate(full_text)
    zh_segments = split_translation(zh_translation, text_blocks)
    
    zh_srt = f"{output_dir}/subtitle-zh.srt"
    with open(zh_srt, 'w', encoding='utf-8') as f:
        for i, (block, (en_text, _)) in enumerate(zip(subtitle_blocks, text_blocks)):
            for line in block:
                f.write(line)
            f.write(zh_segments[i] + '\n\n')
    
    print(f"   ✓ 中文字幕: {zh_srt}")
    
    # 4. 生成学习数据
    print("📚 步骤 4：生成学习数据...")
    labels_json = f"{output_dir}/labels.json"
    print(f"   ✓ 词汇标签: {labels_json}")
    
    print("\n✅ 处理完成！")
    return {
        'srt': srt_path,
        'zh_srt': zh_srt,
        'labels': labels_json
    }

# 使用
output = process_video_complete('video.mp4', model='base')
```

### 示例 2：批量处理字幕文件

```python
from whisper.core.label import Labeler
import os
import json

def batch_label_subtitles(subtitle_dir, output_dir):
    """批量为字幕文件生成词汇标签"""
    
    labeler = Labeler()
    results = {}
    
    for filename in os.listdir(subtitle_dir):
        if not filename.endswith('.srt'):
            continue
        
        srt_path = os.path.join(subtitle_dir, filename)
        print(f"处理: {filename}")
        
        result = labeler.process_subtitle_file(srt_path)
        results[filename] = {
            'blocks': len(result['blocks']),
            'words': len(result['word_map']),
            'output': result['path'] + '-labels.json'
        }
    
    # 保存汇总
    summary_path = os.path.join(output_dir, 'batch_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 批处理完成：{summary_path}")
    return results

# 使用
batch_label_subtitles('./subtitles', './output')
```

### 示例 3：提取特定难度的词汇

```python
from whisper.core.label import Labeler
from whisper.utils.vocab_level import VocabLevelChecker, VocabLevel

def extract_new_words(srt_path, target_level='cet6'):
    """提取超出用户词汇等级的新单词"""
    
    labeler = Labeler(user_vocab_level=target_level)
    result = labeler.process_subtitle_file(srt_path)
    
    # 获取所有新单词
    new_words = []
    for word, entry in result['word_map'].items():
        if entry.get('collins') or entry.get('oxford'):
            # 有标记表示是较难的单词
            new_words.append({
                'word': word,
                'translation': entry['translation'],
                'definition': entry['definition'],
                'phonetic': entry['phonetic']
            })
    
    return new_words

# 使用
new_words = extract_new_words('subtitle.srt', target_level='cet4')
for word in new_words[:10]:
    print(f"{word['word']}: {word['translation']}")
```

---

## 常见问题

### Q1：如何修改翻译 API Key？

```python
# 编辑 core/translator.py
# 找到这几行并修改：
YOUDAO_APP_KEY = 'your_app_key'
YOUDAO_APP_SECRET = 'your_app_secret'
```

### Q2：如何使用自定义词典？

```python
from whisper.core.label import Labeler

# 指定自定义词典路径
labeler = Labeler(dict_csv_path='/path/to/custom/dict.csv')
result = labeler.process_subtitle_file('subtitle.srt')
```

### Q3：词汇标注的输出文件在哪里？

输出文件默认位置：
```
输入文件：subtitle.srt
输出文件：subtitle-labels.json  (同目录)
```

可以指定输出路径：
```python
result = labeler.process_subtitle_file(
    subtitle_path='input.srt',
    out_json='custom/path/output.json'
)
```

### Q4：如何处理其他语言的字幕？

```python
# 翻译时指定源语言
zh_translation = youdao_translate(
    text,
    from_lang='ja',  # 日语
    to_lang='zh-CHS'
)
```

### Q5：GUI 运行报错怎么办？

检查以下几点：
1. 确保在虚拟环境中：`conda activate whisper-env`
2. 检查依赖：`pip install ffmpeg-python requests`
3. 查看错误日志：`whisper_translate.log` 或 `ffmpeg_error.log`

---

## 模块依赖关系

```
whisper (主包)
├── core/
│   ├── label.py (依赖：utils.stardict, utils.vocab_level)
│   └── translator.py (依赖：requests)
├── utils/
│   ├── stardict.py
│   ├── vocab_level.py
│   ├── linguist.py
│   ├── dict_utils.py
│   └── del_bfz.py
├── gui/
│   └── whisper.py (依赖：core.label, core.translator, ffmpeg)
└── data/
    └── *.csv, *.txt (词典数据)
```

---

## 总结

| 功能 | 主要模块 | 快速示例 |
|-----|--------|--------|
| 词汇标注 | `core.label` | `Labeler().process_subtitle_file('srt')` |
| 翻译 | `core.translator` | `youdao_translate('text')` |
| 难度评估 | `utils.vocab_level` | `VocabLevelChecker(level).is_word_in_level('word')` |
| 词典查询 | `utils.stardict` | `DictCsv('csv').query('word')` |
| GUI 应用 | `gui.whisper` | `python -m whisper.gui.whisper` |
| 字幕嵌入 | `gui.whisper` | `embed_subtitles('video', 'srt')` |
