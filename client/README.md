# VideoLingo Backend - 字幕解析模块

## 功能说明

本模块实现了使用 pysubs2 解析字幕文件（srt/ass等格式），并将字幕按句对齐，输出句级 JSON 数据。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```python
from src.subtitle_parser import SubtitleParser

# 创建解析器实例
parser = SubtitleParser()

# 解析字幕文件
result = parser.parse_subtitle_file("path/to/subtitle.srt")

# 输出结果
print(result)
```

## 输出格式

输出为句级 JSON 数据，包含以下字段：

```json
{
  "sentences": [
    {
      "index": 0,
      "start": 1.5,
      "end": 4.2,
      "text": "这是第一句话。",
      "video_timestamp": "00:00:01,500 --> 00:00:04,200"
    }
  ],
  "total_sentences": 1,
  "duration": 2.7
}
```

## 字段说明

- `index`: 句子索引（从0开始）
- `start`: 句子开始时间（秒）
- `end`: 句子结束时间（秒）
- `text`: 句子文本内容
- `video_timestamp`: 视频时间戳（原始格式）
- `total_sentences`: 总句数
- `duration`: 总时长（秒）
