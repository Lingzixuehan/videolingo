# Whisper 模块快速参考

## 导入方式

```python
# 推荐方式 - 直接导入
from whisper import Labeler, youdao_translate, SubtitleParser

# 完整导入 - 按需导入具体功能
from whisper.core.label import Labeler
from whisper.core.translator import youdao_translate, collect_subtitle_blocks, split_translation
from whisper.core.subtitle_parser import SubtitleParser
from whisper.utils.stardict import DictCsv
from whisper.utils.vocab_level import VocabLevelChecker, VocabLevel
from whisper.gui.whisper import embed_subtitles
```

---

## 常用场景速查表

### 场景 1️⃣ 我想解析多种格式的字幕文件（SRT/ASS/VTT/SSA/SUB）

```python
from whisper import SubtitleParser

# 初始化解析器
parser = SubtitleParser()

# 解析任意格式的字幕
result = parser.parse_subtitle_file('video.srt')
# 或 parser.parse_subtitle_file('video.ass')
# 或 parser.parse_subtitle_file('video.vtt')

# 访问解析结果
print(f"总句数: {result['total_sentences']}")
print(f"总时长: {result['duration']} 秒")

# 遍历句子
for sentence in result['sentences']:
    print(f"{sentence['start']}s: {sentence['text']}")
```

**支持格式：** SRT, ASS, SSA, SUB, VTT

---

### 场景 2️⃣ 我想将字幕保存为 JSON 格式

```python
from whisper import SubtitleParser

parser = SubtitleParser()

# 解析并保存为 JSON
json_file = parser.parse_and_save_json('subtitle.srt')
print(f"已保存到: {json_file}")  # subtitle.json
```

---

### 场景 3️⃣ 我想按时间查询字幕

```python
from whisper import SubtitleParser

parser = SubtitleParser()
result = parser.parse_subtitle_file('video.srt')

# 查询特定时间的字幕
current_time = 30.5  # 秒
subtitle = parser.get_sentence_at_time(result['sentences'], current_time)

if subtitle:
    print(f"当前字幕: {subtitle['text']}")
```

---

### 场景 4️⃣ 我想为 SRT 字幕添加词汇标注

```python
from whisper import Labeler

labeler = Labeler()
result = labeler.process_subtitle_file('subtitle.srt')
# 输出：subtitle-labels.json
```

**输出文件包含：**
- 每个字幕块的词汇信息
- 每个单词的音标、定义、翻译
- 全局词汇映射表

---

### 场景 5️⃣ 我想翻译英文字幕为中文

```python
from whisper.core.translator import youdao_translate, collect_subtitle_blocks, split_translation

# 收集字幕块
subtitle_blocks, text_blocks = collect_subtitle_blocks('input.srt')

# 翻译
full_text = ' '.join(text for text, _ in text_blocks)
zh_translation = youdao_translate(full_text, from_lang='en', to_lang='zh-CHS')

# 分配翻译到各块
zh_segments = split_translation(zh_translation, text_blocks)

# 写入文件
base = 'input'
with open(f'{base}-zh.srt', 'w', encoding='utf-8') as f:
    for i, block in enumerate(subtitle_blocks):
        for line in block:
            f.write(line)
        f.write(zh_segments[i] + '\n\n')
```

**输出文件：**
- `input-zh.srt` - 中文字幕

---

### 场景 6️⃣ 我想把字幕嵌入到视频

```python
from whisper.gui.whisper import embed_subtitles

output = embed_subtitles('video.mp4', 'subtitle-zh.srt')
print(f"输出：{output}")  # video_with_subs.mp4
```

---

### 场景 7️⃣ 我想查询单个单词的信息

```python
from whisper import Labeler

labeler = Labeler()
entry = labeler.lookup('serendipity')

print(f"单词: {entry['word']}")
print(f"音标: {entry['phonetic']}")
print(f"翻译: {entry['translation']}")
print(f"定义: {entry['definition']}")
```

---

### 场景 8️⃣ 我想从字幕中提取新单词（CET-4 级以上）

```python
from whisper import Labeler

labeler = Labeler(user_vocab_level='cet4')
result = labeler.process_subtitle_file('subtitle.srt')

new_words = result['word_map']
for word in list(new_words.keys())[:20]:
    print(f"{word}: {new_words[word]['translation']}")
```

---

### 场景 9️⃣ 我想在 GUI 中处理视频

```bash
# 激活虚拟环境
conda activate whisper-env

# 启动 GUI
python -m whisper.gui.whisper
```

**步骤：**
1. 点击 "..." 选择视频文件
2. 选择 Whisper 模型（推荐：base）
3. 点击 "提取并嵌入字幕"
4. 等待处理完成

**输出文件：**
- `video.srt` - 原始英文字幕
- `video-zh.srt` - 中文字幕
- `video-bi.srt` - 双语字幕
- `video-labels.json` - 词汇标签
- `video_with_subs.mp4` - 嵌入字幕的视频

---

### 场景 🔟 我想批量处理多个字幕文件

```python
from whisper import Labeler
import os

labeler = Labeler()
input_dir = './subtitles'
output_dir = './output'

for filename in os.listdir(input_dir):
    if filename.endswith('.srt'):
        srt_path = os.path.join(input_dir, filename)
        result = labeler.process_subtitle_file(srt_path)
        print(f"✓ {filename}: {len(result['word_map'])} 个单词")
```

---

### 场景 1️⃣1️⃣ 我想检查单词难度等级

```python
from whisper.utils.vocab_level import VocabLevelChecker, VocabLevel

# 假设用户是 CET-4 水平
checker = VocabLevelChecker(VocabLevel.CET4)

# 检查单词是否在词汇表中
print(checker.is_word_in_level('hello'))        # True (基础词)
print(checker.is_word_in_level('serendipity'))  # False (超出 CET-4)
```

---

## 各模块文件速查

| 功能 | 文件位置 | 主要类/函数 |
|-----|--------|----------|
| 字幕解析 | `core/subtitle_parser.py` | `SubtitleParser` |
| 词汇标注 | `core/label.py` | `Labeler` |
| 翻译 | `core/translator.py` | `youdao_translate`, `collect_subtitle_blocks`, `split_translation` |
| 词典 | `utils/stardict.py` | `DictCsv` |
| 难度评估 | `utils/vocab_level.py` | `VocabLevelChecker`, `VocabLevel` |
| GUI | `gui/whisper.py` | `embed_subtitles`, GUI 窗口 |
| 语言学 | `utils/linguist.py` | 词形变换、词根提取 |
| 字典工具 | `utils/dict_utils.py` | 字典操作工具 |

---

## API 常用参数

### Labeler.__init__()

```python
Labeler(
    dict_csv_path=None,      # 词典文件路径，默认使用 data/ecdict.csv
    user_vocab_level='cet4'  # 用户词汇等级：basic, cet4, cet6, toefl, ielts, gre, advanced
)
```

### Labeler.process_subtitle_file()

```python
labeler.process_subtitle_file(
    subtitle_path,  # SRT 字幕文件路径
    out_json=None   # 输出 JSON 路径，默认：{subtitle_path}-labels.json
)
```

### youdao_translate()

```python
youdao_translate(
    q,           # 要翻译的文本
    from_lang='en',   # 源语言代码
    to_lang='zh-CHS'  # 目标语言代码
)
```

**支持的语言代码：**
- `'en'` - 英语
- `'zh-CHS'` - 简体中文
- `'zh-CHT'` - 繁体中文
- `'ja'` - 日语
- `'ko'` - 韩语

---

## 错误排查

| 错误信息 | 原因 | 解决方案 |
|--------|------|--------|
| `ModuleNotFoundError: No module named 'whisper'` | 模块未安装或路径错误 | 检查是否在虚拟环境中，检查工作目录 |
| `FileNotFoundError: 未找到词典文件` | 词典文件路径错误 | 检查 `data/ecdict.csv` 是否存在 |
| `FFmpeg not found` | FFmpeg 未安装 | 运行 `conda install ffmpeg -c conda-forge` |
| `翻译返回空字符串` | API 调用失败 | 检查网络连接，检查 API Key 是否正确 |
| `GUI 无法启动` | 依赖缺失或环境问题 | 检查 tkinter 是否安装，检查虚拟环境 |

---

## 性能建议

| 操作 | 耗时 | 优化建议 |
|-----|------|--------|
| 词汇标注 | ~100ms/单词 | 使用精简词典 (ecdict.mini.csv)，但准确度下降 |
| 翻译 | ~500ms/请求 | 批量翻译比逐句翻译更快 |
| Whisper 提取 | 视频时长的 0.5-2x | 使用更小的模型 (tiny, base) 加快速度 |
| 字幕嵌入 | 视频时长的 1-3x | 使用硬件加速（GPU）如果可用 |

---

## 完整工作流

```
输入视频 (video.mp4)
    ↓
Whisper 提取 (model: base)
    ↓
产生字幕 (video.srt)
    ↓
词汇标注 (Labeler)
    ↓
产生词汇标签 (video-labels.json)
    ↓
翻译 (youdao_translate)
    ↓
产生双语字幕 (video-zh.srt, video-bi.srt)
    ↓
字幕嵌入 (embed_subtitles)
    ↓
输出视频 (video_with_subs.mp4)
```

---

## 下一步

- 📖 详细文档：查看 `README.md`
- 💻 完整示例：查看 `tests/test_vocab_level.py`
- 🎯 实际应用：在 GUI 中尝试处理自己的视频文件
