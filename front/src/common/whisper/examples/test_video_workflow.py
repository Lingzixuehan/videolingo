#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的视频处理工作流测试脚本

测试功能：
1. ✅ 字幕提取功能 - 从视频提取字幕
2. ✅ 字幕解析功能 - 解析字幕文件到 JSON
3. ✅ 字幕嵌入功能 - 将字幕嵌入到视频
4. ✅ 词汇标注功能 - 提取和标注词汇

使用方法:
    python test_video_workflow.py

依赖:
    - openai-whisper
    - ffmpeg-python
    - pysubs2
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入核心模块
try:
    from core.subtitle_parser import SubtitleParser
    from core.label import Labeler
    from core.translator import youdao_translate, collect_subtitle_blocks, split_translation
    from gui.whisper import embed_subtitles
except (ImportError, ValueError) as e:
    try:
        from whisper.core.subtitle_parser import SubtitleParser
        from whisper.core.label import Labeler
        from whisper.core.translator import youdao_translate, collect_subtitle_blocks, split_translation
        from whisper.gui.whisper import embed_subtitles
    except ImportError as e2:
        print(f"❌ 导入失败: {e2}")
        print("确保你在项目根目录运行此脚本")
        sys.exit(1)


class VideoTestWorkflow:
    """视频处理工作流测试类"""
    
    def __init__(self, video_path, output_dir=None):
        """
        初始化工作流
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录（默认为视频同目录的 test_output）
        """
        self.video_path = video_path
        self.video_name = Path(video_path).stem
        
        # 创建输出目录
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(video_path), 'test_output')
        
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # 文件路径
        self.srt_path = os.path.join(self.output_dir, f'{self.video_name}.srt')
        self.json_path = os.path.join(self.output_dir, f'{self.video_name}.json')
        self.labels_path = os.path.join(self.output_dir, f'{self.video_name}-labels.json')
        self.embedded_video_path = os.path.join(self.output_dir, f'{self.video_name}_with_subs.mp4')
        self.report_path = os.path.join(self.output_dir, 'test_report.txt')
        
        self.report = []
        self.add_report(f"🎬 视频处理工作流测试")
        self.add_report(f"=" * 60)
        self.add_report(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.add_report(f"视频文件: {self.video_path}")
        self.add_report(f"输出目录: {self.output_dir}")
        self.add_report("")
    
    def add_report(self, text):
        """添加报告文本"""
        self.report.append(text)
        print(text)
    
    def save_report(self):
        """保存报告到文件"""
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.report))
        self.add_report(f"\n📄 报告已保存: {self.report_path}")
    
    def test_1_extract_subtitles(self):
        """
        测试 1: 字幕提取功能
        使用 OpenAI Whisper 从视频提取英文字幕
        """
        self.add_report("\n" + "=" * 60)
        self.add_report("测试 1️⃣ : 字幕提取功能")
        self.add_report("=" * 60)
        
        try:
            # 检查视频文件
            if not os.path.exists(self.video_path):
                self.add_report(f"❌ 视频文件不存在: {self.video_path}")
                return False
            
            self.add_report(f"📹 视频文件: {self.video_path}")
            self.add_report(f"📏 文件大小: {os.path.getsize(self.video_path) / (1024*1024):.2f} MB")
            
            # 检查 Whisper 是否安装
            try:
                import whisper
                self.add_report(f"✅ Whisper 已安装 (版本: {whisper.__version__})")
            except ImportError:
                self.add_report("❌ Whisper 未安装，请运行: pip install -U openai-whisper")
                return False
            
            # 检查 FFmpeg
            try:
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    self.add_report("✅ FFmpeg 已安装")
                else:
                    self.add_report("⚠️ FFmpeg 可能未正确安装")
            except FileNotFoundError:
                self.add_report("❌ FFmpeg 未安装，请运行: pip install ffmpeg-python")
                return False
            
            # 运行 Whisper
            self.add_report("\n🔄 运行 Whisper 提取字幕...")
            self.add_report("(这可能需要几分钟，取决于视频长度和模型大小)")
            
            cmd = [
                sys.executable, '-m', 'whisper',
                self.video_path,
                '--model', 'base',
                '--language', 'English',
                '--task', 'translate',
                '--output_format', 'srt',
                '--output_dir', self.output_dir,
                '--verbose', 'False'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0 and os.path.exists(self.srt_path):
                self.add_report(f"✅ 字幕提取成功")
                self.add_report(f"📄 字幕文件: {self.srt_path}")
                
                # 统计字幕信息
                with open(self.srt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    subtitle_count = content.count('\n\n')
                    lines = len(content.split('\n'))
                
                self.add_report(f"📊 字幕块数: {subtitle_count}")
                self.add_report(f"📝 总行数: {lines}")
                
                # 显示前几行
                self.add_report("\n📋 字幕预览 (前 3 块):")
                lines = content.split('\n')
                preview_lines = 0
                for i, line in enumerate(lines[:30]):
                    if line.strip():
                        self.add_report(f"   {line}")
                        preview_lines += 1
                    if preview_lines >= 12:  # 约 3 块字幕
                        break
                
                return True
            else:
                self.add_report(f"❌ 字幕提取失败")
                if result.stderr:
                    self.add_report(f"错误信息: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            self.add_report(f"❌ 异常错误: {str(e)}")
            return False
    
    def test_2_parse_subtitles(self):
        """
        测试 2: 字幕解析功能
        使用 SubtitleParser 将字幕文件解析为结构化 JSON
        """
        self.add_report("\n" + "=" * 60)
        self.add_report("测试 2️⃣ : 字幕解析功能")
        self.add_report("=" * 60)
        
        try:
            # 检查字幕文件
            if not os.path.exists(self.srt_path):
                self.add_report(f"⚠️ 字幕文件不存在，跳过此测试")
                self.add_report(f"   预期路径: {self.srt_path}")
                return False
            
            self.add_report(f"📄 输入字幕: {self.srt_path}")
            
            # 创建解析器
            parser = SubtitleParser()
            self.add_report("✅ SubtitleParser 已初始化")
            
            # 解析字幕
            self.add_report("\n🔄 解析字幕文件...")
            result = parser.parse_subtitle_file(self.srt_path)
            
            # 检查结果
            if result and 'sentences' in result:
                self.add_report(f"✅ 字幕解析成功")
                
                # 统计信息
                total_sentences = result['total_sentences']
                duration = result['duration']
                format_type = result['format']
                
                self.add_report(f"\n📊 解析结果统计:")
                self.add_report(f"   总句数: {total_sentences}")
                self.add_report(f"   总时长: {duration:.2f} 秒 ({duration/60:.1f} 分钟)")
                self.add_report(f"   格式: {format_type}")
                
                if total_sentences > 0:
                    avg_duration = duration / total_sentences
                    self.add_report(f"   平均时长: {avg_duration:.2f} 秒/句")
                
                # 保存为 JSON
                self.add_report(f"\n💾 保存解析结果为 JSON...")
                json_result = parser.parse_and_save_json(self.srt_path, self.json_path)
                self.add_report(f"✅ JSON 已保存: {json_result}")
                
                # 显示前几个句子的预览
                self.add_report(f"\n📋 字幕句子预览 (前 5 句):")
                for i, sentence in enumerate(result['sentences'][:5]):
                    start = sentence['start']
                    end = sentence['end']
                    text = sentence['text'][:50]  # 只显示前 50 个字符
                    self.add_report(f"   [{i+1}] {start:.2f}s - {end:.2f}s: {text}...")
                
                return True
            else:
                self.add_report(f"❌ 字幕解析失败: 无效的结果格式")
                return False
                
        except Exception as e:
            self.add_report(f"❌ 异常错误: {str(e)}")
            import traceback
            self.add_report(f"   {traceback.format_exc()}")
            return False
    
    def test_3_embed_subtitles(self):
        """
        测试 3: 字幕嵌入功能
        使用 FFmpeg 将字幕嵌入到视频
        """
        self.add_report("\n" + "=" * 60)
        self.add_report("测试 3️⃣ : 字幕嵌入功能")
        self.add_report("=" * 60)
        
        try:
            # 检查字幕文件
            if not os.path.exists(self.srt_path):
                self.add_report(f"⚠️ 字幕文件不存在，跳过此测试")
                self.add_report(f"   预期路径: {self.srt_path}")
                return False
            
            self.add_report(f"📹 视频文件: {self.video_path}")
            self.add_report(f"📄 字幕文件: {self.srt_path}")
            
            # 嵌入字幕
            self.add_report("\n🔄 使用 FFmpeg 嵌入字幕...")
            output_video = embed_subtitles(self.video_path, self.srt_path)
            
            if output_video and os.path.exists(output_video):
                output_size = os.path.getsize(output_video) / (1024*1024)
                self.add_report(f"✅ 字幕嵌入成功")
                self.add_report(f"📹 输出视频: {output_video}")
                self.add_report(f"📏 文件大小: {output_size:.2f} MB")
                return True
            else:
                self.add_report(f"❌ 字幕嵌入失败")
                return False
                
        except Exception as e:
            self.add_report(f"❌ 异常错误: {str(e)}")
            import traceback
            self.add_report(f"   {traceback.format_exc()}")
            return False
    
    def test_4_annotate_vocabulary(self):
        """
        测试 4: 词汇标注功能
        使用 Labeler 从字幕中提取和标注词汇
        """
        self.add_report("\n" + "=" * 60)
        self.add_report("测试 4️⃣ : 词汇标注功能")
        self.add_report("=" * 60)
        
        try:
            # 检查字幕文件
            if not os.path.exists(self.srt_path):
                self.add_report(f"⚠️ 字幕文件不存在，跳过此测试")
                self.add_report(f"   预期路径: {self.srt_path}")
                return False
            
            self.add_report(f"📄 输入字幕: {self.srt_path}")
            
            # 创建标注器
            self.add_report("\n🔄 初始化 Labeler...")
            
            # 查找词典文件
            dict_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'ecdict.csv'
            )
            
            if os.path.exists(dict_path):
                self.add_report(f"✅ 词典文件已找到: {dict_path}")
                labeler = Labeler(dict_csv_path=dict_path)
            else:
                self.add_report(f"⚠️ 词典文件未找到，使用默认词典")
                labeler = Labeler()
            
            # 处理字幕文件
            self.add_report("\n🔄 提取和标注词汇...")
            result = labeler.process_subtitle_file(
                self.srt_path,
                out_json=self.labels_path
            )
            
            if result:
                self.add_report(f"✅ 词汇标注成功")
                
                # 统计信息
                blocks_count = len(result.get('blocks', []))
                word_count = len(result.get('word_map', {}))
                output_file = result.get('path')
                
                self.add_report(f"\n📊 标注结果统计:")
                self.add_report(f"   字幕块数: {blocks_count}")
                self.add_report(f"   提取词汇数: {word_count}")
                self.add_report(f"   输出文件: {output_file}")
                
                # 显示前几个词汇
                if word_count > 0:
                    self.add_report(f"\n📚 提取的词汇示例 (前 10 个):")
                    word_map = result.get('word_map', {})
                    for i, (word, info) in enumerate(list(word_map.items())[:10]):
                        trans = info.get('translation', '未知')
                        phonetic = info.get('phonetic', '/')
                        self.add_report(f"   [{i+1}] {word} /{phonetic}/ - {trans}")
                
                # 检查并加载输出 JSON
                if output_file and os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        labels_data = json.load(f)
                    self.add_report(f"\n✅ 标注文件已保存: {output_file}")
                    self.add_report(f"   文件大小: {os.path.getsize(output_file) / 1024:.1f} KB")
                
                return True
            else:
                self.add_report(f"❌ 词汇标注失败")
                return False
                
        except Exception as e:
            self.add_report(f"❌ 异常错误: {str(e)}")
            import traceback
            self.add_report(f"   {traceback.format_exc()}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        results = {}
        
        # 测试 1: 字幕提取
        results['extract_subtitles'] = self.test_1_extract_subtitles()
        
        # 测试 2: 字幕解析
        results['parse_subtitles'] = self.test_2_parse_subtitles()
        
        # 测试 3: 字幕嵌入
        results['embed_subtitles'] = self.test_3_embed_subtitles()
        
        # 测试 4: 词汇标注
        results['annotate_vocabulary'] = self.test_4_annotate_vocabulary()
        
        # 总结
        self.add_report("\n" + "=" * 60)
        self.add_report("📊 测试总结")
        self.add_report("=" * 60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            display_name = {
                'extract_subtitles': '字幕提取',
                'parse_subtitles': '字幕解析',
                'embed_subtitles': '字幕嵌入',
                'annotate_vocabulary': '词汇标注'
            }.get(name, name)
            self.add_report(f"{status} - {display_name}")
        
        self.add_report("")
        self.add_report(f"总体通过率: {passed}/{total} ({100*passed/total:.1f}%)")
        
        self.add_report(f"\n📁 输出文件:")
        self.add_report(f"   字幕文件: {self.srt_path}")
        self.add_report(f"   JSON 文件: {self.json_path}")
        self.add_report(f"   词汇标注: {self.labels_path}")
        self.add_report(f"   嵌入视频: {self.embedded_video_path}")
        self.add_report(f"   报告文件: {self.report_path}")
        
        self.add_report(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存报告
        self.save_report()
        
        return results


def main():
    """主函数"""
    # 视频文件路径
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(examples_dir, 'input.mp4')
    
    # 检查视频文件
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        print("请确保 input.mp4 在 examples 目录中")
        sys.exit(1)
    
    print(f"✅ 找到视频文件: {video_path}")
    print()
    
    # 创建工作流
    workflow = VideoTestWorkflow(video_path)
    
    # 运行所有测试
    results = workflow.run_all_tests()
    
    # 返回状态码
    if all(results.values()):
        print("\n✅ 所有测试都通过了！")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败，请查看报告了解详情")
        sys.exit(1)


if __name__ == '__main__':
    main()
