from urllib import parse
import requests
import re
from urllib import parse
import requests
import re
import html
import sys
import time
import hashlib
import json

# 固定使用有道翻译接口
YOUDAO_URL = 'https://openapi.youdao.com/api'
YOUDAO_APP_KEY = '60dc3c8a3e2f8459'
YOUDAO_APP_SECRET = 'FqMygHNm7dqjFdSkupskpMSIpNfNlcIF'


def youdao_translate(q: str, from_lang: str = 'en', to_lang: str = 'zh-CHS') -> str:
    """使用有道开放接口翻译单条文本。

    使用简单签名 (md5(appKey + q + salt + appSecret))。
    返回翻译后的文本（若失败返回空字符串）。
    """
    if not q or q.strip() == '':
        return ''
    salt = str(int(time.time() * 1000))
    sign_str = YOUDAO_APP_KEY + q + salt + YOUDAO_APP_SECRET
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    data = {
        'q': q,
        'from': from_lang,
        'to': to_lang,
        'appKey': YOUDAO_APP_KEY,
        'salt': salt,
        'sign': sign,
    }
    try:
        resp = requests.post(YOUDAO_URL, data=data, timeout=8)
        if resp.status_code != 200:
            return ''
        j = resp.json()
        # 有道返回的翻译通常在 'translation' 字段
        if 'translation' in j and isinstance(j['translation'], list):
            return ''.join(j['translation'])
        # 兼容老接口字段或其他格式
        if 'errorCode' in j and j.get('errorCode') != '0':
            return ''
        return ''
    except Exception:
        return ''


def _is_text_line(line: str) -> bool:
    """判断是否为需要翻译的字幕文本行（非数字序号、非时间戳、非空行）。"""
    s = line.strip()
    if s == '':
        return False
    # 时间戳行通常包含 -->
    if '-->' in s:
        return False
    # 如果整行是数字序号
    if s.isdigit():
        return False
    return True


def collect_subtitle_blocks(file_path: str) -> tuple[list, list]:
    """处理SRT文件，收集所有字幕块的信息。
    
    返回两个列表：
    1. subtitle_blocks: 每个元素包含字幕块的基本信息（序号、时间戳行）
    2. text_blocks: 每个元素是一个元组(原文本, 字符长度)
    """
    subtitle_blocks = []  # 存储字幕块的基本信息（序号和时间戳）
    text_blocks = []      # 存储文本信息和长度
    current_block = []
    current_text = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.isdigit():  # 新字幕块的开始
                if current_block and current_text:  # 保存前一个字幕块
                    subtitle_blocks.append(current_block)
                    text = ' '.join(current_text)
                    text_blocks.append((text, len(text)))
                    current_block = []
                    current_text = []
                current_block.append(line + '\n')  # 序号
                i += 1
                if i < len(lines):  # 时间戳行
                    current_block.append(lines[i])
                    i += 1
                    while i < len(lines) and _is_text_line(lines[i]):  # 文本行
                        text_line = lines[i].rstrip('\n')
                        current_text.append(text_line)
                        i += 1
            else:
                i += 1
                
    # 处理最后一个字幕块
    if current_block and current_text:
        subtitle_blocks.append(current_block)
        text = ' '.join(current_text)
        text_blocks.append((text, len(text)))
    
    return subtitle_blocks, text_blocks


def split_translation(translation: str, text_blocks: list) -> list:
    """根据原文本长度比例分配翻译文本。
    
    Args:
        translation: 整体翻译后的中文文本
        text_blocks: 原文本块列表，每个元素是(文本, 长度)元组
    
    Returns:
        list: 分割后的中文翻译列表
    """
    # 计算所有原文本的总长度
    total_length = sum(length for _, length in text_blocks)
    
    # 如果翻译为空，返回对应数量的空字符串
    if not translation:
        return [''] * len(text_blocks)
        
    result = []
    translation_length = len(translation)
    current_pos = 0
    
    # 根据原文长度比例分配翻译文本
    for _, length in text_blocks:
        # 计算应分配的字符数
        ratio = length / total_length
        chars_to_take = round(translation_length * ratio)
        
        # 确保不会超出字符串范围
        if current_pos + chars_to_take > translation_length:
            chars_to_take = translation_length - current_pos
            
        # 提取对应的翻译文本段
        if chars_to_take > 0 and current_pos < translation_length:
            segment = translation[current_pos:current_pos + chars_to_take]
            current_pos += chars_to_take
        else:
            segment = ''
            
        result.append(segment)
    
    # 如果还有剩余文本，添加到最后一段
    if current_pos < translation_length:
        result[-1] += translation[current_pos:]
        
    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python whisperTranslator.py <srt_file_path>')
        sys.exit(1)

    file_path = sys.argv[1]
    base = file_path[:file_path.rfind('.')]
    zh_path = base + '-zh.srt'
    bi_path = base + '-bi.srt'

    # 处理SRT文件，收集所有字幕块信息
    subtitle_blocks, text_blocks = collect_subtitle_blocks(file_path)
    
    # 将所有英文文本整合在一起进行翻译
    full_text = ' '.join(text for text, _ in text_blocks)
    zh_translation = youdao_translate(full_text, from_lang='en', to_lang='zh-CHS')
    
    # 根据原文长度比例分配翻译文本
    zh_segments = split_translation(zh_translation, text_blocks)
    
    with open(zh_path, 'w', encoding='utf-8') as wf_zh, \
         open(bi_path, 'w', encoding='utf-8') as wf_bi:
        
        # 写入每个字幕块
        for i, (block, (en_text, _)) in enumerate(zip(subtitle_blocks, text_blocks)):
            # 获取当前块的中文翻译
            zh_text = zh_segments[i]
            
            # 写入中文字幕文件
            for line in block:  # 写入序号和时间戳行
                wf_zh.write(line)
            wf_zh.write(zh_text + '\n\n')  # 写入翻译后的文本
            
            # 写入双语字幕文件
            for line in block:  # 写入序号和时间戳行
                wf_bi.write(line)
            wf_bi.write(en_text + '\n')  # 写入英文原文
            wf_bi.write(zh_text + '\n\n')  # 写入中文翻译

    print(f'生成中文字幕: {zh_path}')
    print(f'生成中英双语字幕: {bi_path}')

    print(f'生成中文字幕: {zh_path}')
    print(f'生成中英双语字幕: {bi_path}')

    print(f'生成中文字幕: {zh_path}')
    print(f'生成中英双语字幕: {bi_path}')

