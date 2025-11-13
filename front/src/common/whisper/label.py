import os
import re
import json
import sys
from typing import List, Tuple, Dict, Any

# 使用同目录下的 stardict.py 中的 DictCsv
try:
    import stardict
except Exception:
    stardict = None


def _tokenize(text: str) -> List[str]:
    """将一句话分词为英文单词列表，保留缩写/撇号（如 there's）。"""
    # 只抓取字母和撇号组合
    tokens = re.findall(r"[A-Za-z']+", text)
    return tokens


def _generate_candidates(word: str) -> List[str]:
    """为单词生成若干候选查找形式（lower, 移除 's, 去掉复数 s 等）。"""
    w = word
    cand = []
    lw = w.lower()
    cand.append(lw)
    # 去除首尾撇号
    if lw.startswith("'") or lw.endswith("'"):
        cand.append(lw.strip("'"))
    # 去除 's
    if lw.endswith("'s"):
        cand.append(lw[:-2])
    if lw.endswith("s") and len(lw) > 3:
        cand.append(lw[:-1])
    # 处理缩写 like dont -> don't not handled; keep as is
    # 去掉非字母
    cand.append(re.sub("[^a-z]", "", lw))
    # 去重并保持顺序
    seen = set()
    res = []
    for c in cand:
        if c and c not in seen:
            seen.add(c)
            res.append(c)
    return res


class Labeler:
    def __init__(self, dict_csv_path: str = None):
        self.dict_csv_path = dict_csv_path or os.path.join(os.path.dirname(__file__), 'ecdict.csv')
        self._dict = None
        if stardict is None:
            raise RuntimeError('stardict 模块不可用，无法加载词典')
        self._load_dict()

    def _load_dict(self):
        if not os.path.exists(self.dict_csv_path):
            raise FileNotFoundError(f'未找到词典文件: {self.dict_csv_path}')
        # DictCsv 接口在 stardict.py 中实现
        self._dict = stardict.DictCsv(self.dict_csv_path)

    def lookup(self, word: str) -> Dict[str, Any]:
        """查找单词并返回词典项（保证返回包含必要字段的 dict）。"""
        candidates = _generate_candidates(word)
        for c in candidates:
            try:
                rec = self._dict.query(c)
            except Exception:
                rec = None
            if rec:
                # rec 已经是字典对象，直接返回重要字段（确保存在）
                # 复制并规范化字段
                entry = {
                    'word': rec.get('word') or c,
                    'phonetic': rec.get('phonetic') or '',
                    'definition': rec.get('definition') or '',
                    'translation': rec.get('translation') or '',
                    'pos': rec.get('pos') or '',
                    'collins': rec.get('collins') or '',
                    'oxford': rec.get('oxford') or '',
                    'tag': rec.get('tag') or '',
                    'bnc': rec.get('bnc') or '',
                    'frq': rec.get('frq') or '',
                    'exchange': rec.get('exchange') or '',
                    'detail': rec.get('detail') or '',
                    'audio': rec.get('audio') or '',
                }
                return entry
        # 未找到任何匹配，返回空白结构但包含原词
        return {
            'word': word,
            'phonetic': '',
            'definition': '',
            'translation': '',
            'pos': '',
            'collins': '',
            'oxford': '',
            'tag': '',
            'bnc': '',
            'frq': '',
            'exchange': '',
            'detail': '',
            'audio': '',
        }

    def process_subtitle_file(self, subtitle_path: str, out_json: str = None) -> Dict[str, Any]:
        """处理 SRT/ASS 字幕文件，生成每句的词汇释义与标签并写入 JSON。

        返回生成的 JSON 数据（字典）。
        """
        # 读取字幕并抽取每个字幕块的时间和文本
        blocks = []  # each: dict(index, start, end, text)
        if not os.path.exists(subtitle_path):
            raise FileNotFoundError(subtitle_path)

        with open(subtitle_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.isdigit():
                index = int(line)
                i += 1
                if i >= len(lines):
                    break
                times = lines[i].strip()
                start, end = ('', '')
                m = re.match(r"(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})", times)
                if m:
                    start, end = m.group(1), m.group(2)
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip() != '':
                    text_lines.append(lines[i].rstrip('\n'))
                    i += 1
                # 跳过空行
                while i < len(lines) and lines[i].strip() == '':
                    i += 1
                text = ' '.join([t.strip() for t in text_lines])
                blocks.append({'index': index, 'start': start, 'end': end, 'text': text})
            else:
                i += 1

        # 对每个块中的单词进行查找
        label_blocks = []
        word_map = {}  # unique word -> entry

        for blk in blocks:
            text = blk['text']
            tokens = _tokenize(text)
            words_info = []
            for tok in tokens:
                key = tok
                entry = self.lookup(tok)
                # 记录到 words_info
                words_info.append({'original': key, 'entry': entry})
                # 确保每一个词在 word_map 中
                word_map[key.lower()] = entry
            label_blocks.append({
                'index': blk['index'],
                'start': blk['start'],
                'end': blk['end'],
                'text': blk['text'],
                'words': words_info
            })

        result = {
            'source': os.path.basename(subtitle_path),
            'path': os.path.abspath(subtitle_path),
            'blocks': label_blocks,
            'word_map': word_map
        }

        # 输出 JSON
        if not out_json:
            base = subtitle_path[:subtitle_path.rfind('.')]
            out_json = base + '-labels.json'
        try:
            with open(out_json, 'w', encoding='utf-8') as jf:
                json.dump(result, jf, ensure_ascii=False, indent=2)
        except Exception as e:
            raise

        return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python label.py <subtitle.srt> [ecdict.csv]')
        sys.exit(1)
    srt = sys.argv[1]
    csvp = sys.argv[2] if len(sys.argv) > 2 else None
    lab = Labeler(dict_csv_path=csvp) if csvp else Labeler()
    data = lab.process_subtitle_file(srt)
    print(f'生成标签文件，包含 {len(data["blocks"])} 个字幕块，{len(data["word_map"])} 个单词')
