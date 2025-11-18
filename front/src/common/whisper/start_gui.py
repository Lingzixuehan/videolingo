#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Whisper GUI 快速启动脚本

直接运行：python start_gui.py
或从命令行：python start_gui.py
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动 GUI 应用"""
    
    print("=" * 60)
    print("🎨 Whisper GUI 启动脚本")
    print("=" * 60)
    print()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    gui_file = project_root / "gui" / "whisper.py"
    
    print(f"📂 项目根目录: {project_root}")
    print(f"🖥️  GUI 文件: {gui_file}")
    print()
    
    # 检查 GUI 文件是否存在
    if not gui_file.exists():
        print(f"❌ 错误: 找不到 GUI 文件 {gui_file}")
        return 1
    
    print("🚀 正在启动 GUI...")
    print()
    
    # 启动 GUI
    try:
        # 在项目目录中运行
        os.chdir(str(project_root))
        
        # 直接运行 GUI 脚本
        result = subprocess.run(
            [sys.executable, str(gui_file)],
            cwd=str(project_root)
        )
        
        if result.returncode == 0:
            print()
            print("✅ GUI 应用已退出（正常）")
        else:
            print()
            print(f"⚠️  GUI 应用退出，返回码: {result.returncode}")
            return result.returncode
    
    except KeyboardInterrupt:
        print()
        print("⏹️  GUI 应用已停止")
        return 0
    
    except Exception as e:
        print()
        print(f"❌ 错误: {e}")
        return 1
    
    print()
    print("=" * 60)
    print("感谢使用 Whisper GUI!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
