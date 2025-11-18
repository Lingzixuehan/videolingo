import os
import re
import json
import sys
from typing import List, Tuple, Dict, Any

import os
import re
import json
import sys
from typing import List, Tuple, Dict, Any

# 导入 stardict 词典模块 - 支持多种导入方式
DictCsv = None
try:
    from ..utils.stardict import DictCsv
except (ImportError, ValueError):
    try:
        from whisper.utils.stardict import DictCsv
    except ImportError:
        try:
            # 直接路径导入（当从同目录脚本调用时）
            current_dir = os.path.dirname(os.path.dirname(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            from utils.stardict import DictCsv
        except ImportError:
            pass

# 导入词汇难度分级模块 - 支持多种导入方式
VocabLevelChecker = None
VocabLevel = None
get_level_from_string = None

try:
    from ..utils.vocab_level import VocabLevelChecker, VocabLevel, get_level_from_string
except (ImportError, ValueError):
    try:
        from whisper.utils.vocab_level import VocabLevelChecker, VocabLevel, get_level_from_string
    except ImportError:
        try:
            # 直接路径导入（当从同目录脚本调用时）
            current_dir = os.path.dirname(os.path.dirname(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            from utils.vocab_level import VocabLevelChecker, VocabLevel, get_level_from_string
        except ImportError:
            pass


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
    def __init__(self, dict_csv_path: str = None, user_vocab_level: str = 'cet4'):
        """
        初始化标注器

        Args:
            dict_csv_path: 词典 CSV 文件路径
            user_vocab_level: 用户词汇量等级 ('basic', 'cet4', 'cet6', 'toefl', 'ielts', 'gre', 'advanced')
        """
        if dict_csv_path is None:
            # 构造相对于本文件的 data 目录路径
            current_dir = os.path.dirname(__file__)
            dict_csv_path = os.path.join(current_dir, '..', 'data', 'ecdict.csv')
        
        self.dict_csv_path = dict_csv_path
        self._dict = None
        if DictCsv is None:
            raise RuntimeError('DictCsv 模块不可用，无法加载词典')
        self._load_dict()

        # 初始化词汇难度检查器
        if VocabLevelChecker is not None:
            vocab_level = get_level_from_string(user_vocab_level)
            self.level_checker = VocabLevelChecker(vocab_level)
        else:
            self.level_checker = None

    def _load_dict(self):
        if not os.path.exists(self.dict_csv_path):
            raise FileNotFoundError(f'未找到词典文件: {self.dict_csv_path}')
        # DictCsv 接口在 stardict.py 中实现
        self._dict = DictCsv(self.dict_csv_path)

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
        new_words = []  # 生词列表（超出用户词汇量的单词）

        for blk in blocks:
            text = blk['text']
            tokens = _tokenize(text)
            words_info = []
            for tok in tokens:
                key = tok
                entry = self.lookup(tok)

                # 判断是否超出用户词汇量
                is_new_word = False
                difficulty_label = ''
                if self.level_checker is not None:
                    is_new_word = self.level_checker.is_beyond_level(tok, entry)
                    difficulty_label = self.level_checker.get_difficulty_label(tok, entry)

                # 记录到 words_info，添加难度信息
                word_info = {
                    'original': key,
                    'entry': entry,
                    'is_new': is_new_word,  # 是否超纲
                    'difficulty': difficulty_label  # 难度标签
                }
                words_info.append(word_info)

                # 确保每一个词在 word_map 中，并添加难度信息
                word_key = key.lower()
                if word_key not in word_map:
                    word_map[word_key] = {
                        'entry': entry,
                        'is_new': is_new_word,
                        'difficulty': difficulty_label,
                        'occurrences': []  # 记录出现位置
                    }
                # 记录该词在哪个句子中出现
                word_map[word_key]['occurrences'].append({
                    'sentence_index': blk['index'],
                    'sentence_text': blk['text']
                })

                # 如果是生词，加入生词列表
                if is_new_word and word_key not in [w['word'].lower() for w in new_words]:
                    new_words.append({
                        'word': entry.get('word') or tok,
                        'translation': entry.get('translation', ''),
                        'difficulty': difficulty_label,
                        'first_occurrence': {
                            'sentence_index': blk['index'],
                            'sentence_text': blk['text'],
                            'timestamp': f"{blk['start']} --> {blk['end']}"
                        }
                    })

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
            'word_map': word_map,
            'new_words': new_words,  # 生词列表
            'statistics': {  # 统计信息
                'total_words': len(word_map),
                'new_words_count': len(new_words),
                'coverage_rate': round((len(word_map) - len(new_words)) / len(word_map) * 100, 2) if len(word_map) > 0 else 0
            }
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
        print('用法: python label.py <subtitle.srt> [ecdict.csv] [user_level]')
        print('user_level 可选值: basic, cet4, cet6, toefl, ielts, gre, advanced (默认: cet4)')
        sys.exit(1)
    srt = sys.argv[1]
    csvp = sys.argv[2] if len(sys.argv) > 2 else None
    user_level = sys.argv[3] if len(sys.argv) > 3 else 'cet4'

    lab = Labeler(dict_csv_path=csvp, user_vocab_level=user_level) if csvp else Labeler(user_vocab_level=user_level)
    data = lab.process_subtitle_file(srt)

    print(f'生成标签文件，包含 {len(data["blocks"])} 个字幕块，{len(data["word_map"])} 个单词')
    print(f'统计信息:')
    print(f'  - 总词汇数: {data["statistics"]["total_words"]}')
    print(f'  - 生词数: {data["statistics"]["new_words_count"]}')
    print(f'  - 词汇覆盖率: {data["statistics"]["coverage_rate"]}%')
    print(f'\n前 10 个生词:')
    for i, word in enumerate(data["new_words"][:10], 1):
        print(f'  {i}. {word["word"]} ({word["difficulty"]}) - {word["translation"]}')
