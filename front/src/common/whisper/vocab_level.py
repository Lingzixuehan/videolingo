"""
词汇难度分级配置模块
定义词汇量等级体系和判断逻辑
"""

from typing import Set, List
from enum import Enum


class VocabLevel(Enum):
    """词汇量等级枚举"""
    BASIC = "basic"  # 基础词汇（~1000词）
    CET4 = "cet4"  # 大学英语四级（~4500词）
    CET6 = "cet6"  # 大学英语六级（~6000词）
    TOEFL = "toefl"  # 托福（~8000词）
    IELTS = "ielts"  # 雅思（~8000词）
    GRE = "gre"  # GRE（~12000词）
    ADVANCED = "advanced"  # 高级词汇（全部）


# 词汇量等级层次结构（从低到高，包含关系）
LEVEL_HIERARCHY = {
    VocabLevel.BASIC: set(),
    VocabLevel.CET4: {VocabLevel.BASIC},
    VocabLevel.CET6: {VocabLevel.BASIC, VocabLevel.CET4},
    VocabLevel.TOEFL: {VocabLevel.BASIC, VocabLevel.CET4, VocabLevel.CET6},
    VocabLevel.IELTS: {VocabLevel.BASIC, VocabLevel.CET4, VocabLevel.CET6},
    VocabLevel.GRE: {VocabLevel.BASIC, VocabLevel.CET4, VocabLevel.CET6, VocabLevel.TOEFL, VocabLevel.IELTS},
    VocabLevel.ADVANCED: {VocabLevel.BASIC, VocabLevel.CET4, VocabLevel.CET6, VocabLevel.TOEFL, VocabLevel.IELTS, VocabLevel.GRE}
}


# 标签到等级的映射（词库 tag 字段中的标签）
TAG_TO_LEVEL = {
    'zk': VocabLevel.BASIC,  # 中考
    'gk': VocabLevel.BASIC,  # 高考
    'cet4': VocabLevel.CET4,
    'cet6': VocabLevel.CET6,
    'toefl': VocabLevel.TOEFL,
    'ielts': VocabLevel.IELTS,
    'gre': VocabLevel.GRE,
}


# 常用词库（前1000高频词，无需标注）
# 可以从 BNC/FRQ 词频数据中提取
COMMON_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    # ... 这里只列举部分，实际应包含约1000个高频词
}


class VocabLevelChecker:
    """词汇难度检查器"""

    def __init__(self, user_level: VocabLevel = VocabLevel.CET4):
        """
        初始化检查器

        Args:
            user_level: 用户当前词汇量等级
        """
        self.user_level = user_level
        self.covered_levels = self._get_covered_levels(user_level)

    def _get_covered_levels(self, level: VocabLevel) -> Set[VocabLevel]:
        """获取用户已掌握的所有等级（包含下级）"""
        covered = {level}
        covered.update(LEVEL_HIERARCHY.get(level, set()))
        return covered

    def parse_word_tags(self, tag_string: str) -> Set[VocabLevel]:
        """
        解析词库 tag 字段，返回该词所属的等级集合

        Args:
            tag_string: 词库中的 tag 字段，如 "cet4 cet6"

        Returns:
            该词所属的等级集合
        """
        if not tag_string:
            return set()

        tags = tag_string.lower().split()
        levels = set()

        for tag in tags:
            if tag in TAG_TO_LEVEL:
                levels.add(TAG_TO_LEVEL[tag])

        return levels

    def is_beyond_level(self, word: str, word_entry: dict) -> bool:
        """
        判断单词是否超出用户词汇量

        Args:
            word: 单词原文
            word_entry: 词库查询结果（包含 tag 字段）

        Returns:
            True 表示超纲（需要标注），False 表示在用户掌握范围内
        """
        # 如果是常用词，不标注
        if word.lower() in COMMON_WORDS:
            return False

        # 如果词库中没有信息，保守标注为超纲
        if not word_entry or not word_entry.get('word'):
            return True

        # 获取该词的等级标签
        tag_string = word_entry.get('tag', '')
        word_levels = self.parse_word_tags(tag_string)

        # 如果没有等级标签，根据词频判断
        if not word_levels:
            return self._check_by_frequency(word_entry)

        # 判断该词的所有等级是否都在用户已掌握范围内
        # 如果有任何一个等级超出用户水平，则标注为超纲
        for wl in word_levels:
            if wl not in self.covered_levels:
                return True

        return False

    def _check_by_frequency(self, word_entry: dict) -> bool:
        """
        当词没有等级标签时，根据词频判断是否超纲

        Args:
            word_entry: 词库条目

        Returns:
            True 表示超纲
        """
        # 获取 BNC 词频（British National Corpus）
        # 数值越小表示越常用
        try:
            bnc = int(word_entry.get('bnc', '99999') or '99999')
        except ValueError:
            bnc = 99999

        # 根据用户等级设定词频阈值
        frequency_thresholds = {
            VocabLevel.BASIC: 3000,
            VocabLevel.CET4: 5000,
            VocabLevel.CET6: 8000,
            VocabLevel.TOEFL: 12000,
            VocabLevel.IELTS: 12000,
            VocabLevel.GRE: 20000,
            VocabLevel.ADVANCED: 99999,
        }

        threshold = frequency_thresholds.get(self.user_level, 5000)
        return bnc > threshold

    def get_difficulty_label(self, word: str, word_entry: dict) -> str:
        """
        获取单词的难度标签（用于显示）

        Args:
            word: 单词原文
            word_entry: 词库条目

        Returns:
            难度标签字符串，如 "CET6词汇" "托福词汇" "超纲词"
        """
        if word.lower() in COMMON_WORDS:
            return "常用词"

        if not word_entry or not word_entry.get('word'):
            return "未收录"

        tag_string = word_entry.get('tag', '')
        word_levels = self.parse_word_tags(tag_string)

        if not word_levels:
            # 根据词频判断
            try:
                bnc = int(word_entry.get('bnc', '99999') or '99999')
            except ValueError:
                return "未分级"

            if bnc <= 3000:
                return "高频词"
            elif bnc <= 8000:
                return "中频词"
            else:
                return "低频词"

        # 返回最高等级标签
        level_priority = [
            VocabLevel.GRE,
            VocabLevel.TOEFL,
            VocabLevel.IELTS,
            VocabLevel.CET6,
            VocabLevel.CET4,
            VocabLevel.BASIC
        ]

        for level in level_priority:
            if level in word_levels:
                label_map = {
                    VocabLevel.GRE: "GRE词汇",
                    VocabLevel.TOEFL: "托福词汇",
                    VocabLevel.IELTS: "雅思词汇",
                    VocabLevel.CET6: "六级词汇",
                    VocabLevel.CET4: "四级词汇",
                    VocabLevel.BASIC: "基础词汇"
                }
                return label_map.get(level, "未分级")

        return "未分级"


def get_level_from_string(level_str: str) -> VocabLevel:
    """
    从字符串获取词汇量等级

    Args:
        level_str: 等级字符串，如 "cet4", "toefl"

    Returns:
        VocabLevel 枚举值
    """
    level_str = level_str.lower().strip()

    mapping = {
        'basic': VocabLevel.BASIC,
        'cet4': VocabLevel.CET4,
        'cet6': VocabLevel.CET6,
        'toefl': VocabLevel.TOEFL,
        'ielts': VocabLevel.IELTS,
        'gre': VocabLevel.GRE,
        'advanced': VocabLevel.ADVANCED,
    }

    return mapping.get(level_str, VocabLevel.CET4)  # 默认 CET4
