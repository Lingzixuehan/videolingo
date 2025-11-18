# 🎨 GUI 应用启动完成

## ✅ 状态

**GUI 应用已启动！** 🎉

---

## 🖥️ 启动方式

### 方式 1️⃣ 直接运行脚本

```bash
python gui/whisper.py
```

### 方式 2️⃣ 使用启动脚本

```bash
python start_gui.py
```

### 方式 3️⃣ Windows 批处理 (双击)

```
双击 start_gui.bat
```

### 方式 4️⃣ 后台启动 (不显示终端)

```bash
pythonw gui/whisper.py
```

---

## 📚 应该看什么

根据您的需求选择：

| 需求 | 文档 |
|------|------|
| 快速了解 GUI | [GUI_GUIDE.md](GUI_GUIDE.md) |
| 完整使用指南 | [USAGE_GUIDE.md](USAGE_GUIDE.md) |
| 快速参考 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| 文档导航 | [INDEX.md](INDEX.md) |

---

## 🚀 快速开始

1. **启动 GUI：** `python gui/whisper.py`
2. **选择模型：** 推荐选择 `base`
3. **选择视频：** 点击 "..." 按钮选择视频文件
4. **开始处理：** 点击 "提取并嵌入字幕" 按钮
5. **查看结果：** 检查生成的文件

---

## 📂 文件清单

| 文件 | 用途 |
|------|------|
| `gui/whisper.py` | GUI 主程序 |
| `start_gui.py` | Python 启动脚本 |
| `start_gui.bat` | Windows 批处理启动脚本 |
| `GUI_GUIDE.md` | GUI 使用指南 |

---

## 🎯 功能概览

### 主要功能

✅ **视频字幕提取**
- 使用 Whisper 自动提取英文字幕

✅ **字幕翻译**  
- 使用有道翻译生成中文字幕

✅ **双语字幕**
- 生成英中对照字幕

✅ **字幕嵌入**
- 将字幕直接嵌入视频文件

✅ **词汇标注**
- 自动标注词汇难度和翻译

✅ **本地字幕导入**
- 支持导入已有的 SRT 字幕文件

---

## ⚙️ 支持的功能

### 视频格式
- MP4, AVI, MOV, MKV, FLV, WebM 等

### 字幕格式
- SRT (SubRip)
- 输出：SRT 和 JSON（词汇标注）

### 语言
- 输入：英文（主要）+ 其他语言
- 输出：中文翻译 + 双语字幕

### 模型选择
- tiny (最快)
- base (推荐)
- small (较慢)
- medium (更慢)
- large (最慢，最准)

---

## 💡 使用建议

### 首次使用

1. 选择 `base` 模型（速度和准确度平衡）
2. 选择较短的视频进行测试（1-5 分钟）
3. 查看生成的字幕质量
4. 根据需求调整模型

### 优化性能

- **加快速度：** 选择 `tiny` 或 `base` 模型
- **提高质量：** 选择 `medium` 或 `large` 模型
- **批量处理：** 准备多个视频，逐个处理

### 质量优化

- **音质：** 清晰的音频效果最佳
- **语速：** 中等语速识别率最高
- **字幕质量：** 好的字幕翻译会更准确

---

## 🔗 相关命令

### 验证环境

```bash
# 检查 Tkinter（GUI 框架）
python -m tkinter

# 检查 Whisper
whisper --help

# 检查 FFmpeg
ffmpeg -version
```

### 快速测试

```bash
# 运行快速测试
python quick_test.py

# 运行单元测试
pytest tests/ -v

# 启动 GUI
python gui/whisper.py
```

---

## 📊 系统要求

### 最低配置
- CPU: 双核 2.0 GHz+
- RAM: 4 GB+
- 存储: 2 GB 可用空间

### 推荐配置
- CPU: 四核 2.5 GHz+
- RAM: 8 GB+
- 存储: 5 GB 可用空间
- GPU: NVIDIA CUDA GPU (可选，用于加速)

### 依赖

```bash
pip install openai-whisper
pip install ffmpeg-python
pip install requests
```

---

## 🐛 常见问题

### Q: GUI 窗口不显示

**A:** 检查 Tkinter 是否安装：
```bash
python -m tkinter
```

### Q: 找不到 Whisper 模块

**A:** 安装 Whisper：
```bash
pip install openai-whisper
```

### Q: FFmpeg 错误

**A:** 安装 FFmpeg：
```bash
pip install ffmpeg-python
# 确保 ffmpeg.exe 在 PATH 中
```

### Q: 翻译失败

**A:** 检查网络连接和 API Key

### Q: 处理速度太慢

**A:** 选择更小的模型（tiny/base）

---

## 📖 学习资源

### 新手入门
1. 阅读 [GUI_GUIDE.md](GUI_GUIDE.md)
2. 运行 GUI 进行操作
3. 查看生成的输出文件

### 深入学习
1. 阅读 [USAGE_GUIDE.md](USAGE_GUIDE.md)
2. 了解各个模块的功能
3. 尝试命令行工具

### 开发和扩展
1. 查看 [README.md](README.md)
2. 学习源代码
3. 添加新功能

---

## 🎓 视频处理工作流

```
输入视频
   ↓
选择模型 (tiny/base/small/medium/large)
   ↓
Whisper 提取英文字幕
   ↓
有道翻译翻译为中文
   ↓
生成双语字幕
   ↓
FFmpeg 嵌入字幕
   ↓
输出结果文件：
  ├─ video.srt (英文字幕)
  ├─ video-zh.srt (中文字幕)
  ├─ video-bi.srt (双语字幕)
  ├─ video-labels.json (词汇标注)
  └─ video_with_subs.mp4 (嵌入字幕视频)
```

---

## ✅ 启动检查清单

- [ ] 已阅读本文档
- [ ] 已安装必要依赖 (whisper, ffmpeg-python)
- [ ] 已启动 GUI (`python gui/whisper.py`)
- [ ] 已选择合适的模型
- [ ] 已选择视频文件
- [ ] 已点击 "提取并嵌入字幕" 按钮
- [ ] 已查看生成的输出文件

---

## 🚀 下一步

1. **启动 GUI：** `python gui/whisper.py`
2. **查看指南：** 打开 [GUI_GUIDE.md](GUI_GUIDE.md)
3. **处理视频：** 按照指南步骤操作
4. **查看结果：** 检查输出文件夹

---

## 📞 获取帮助

### 遇到问题？

1. **检查错误信息** - 查看控制台输出
2. **查看 [GUI_GUIDE.md](GUI_GUIDE.md)** - 常见问题解答
3. **检查依赖** - 确保所有必要模块已安装
4. **查看日志** - FFmpeg 错误会记录在 `ffmpeg_error.log`

---

**状态：** ✅ GUI 已启动  
**下一步：** 阅读 [GUI_GUIDE.md](GUI_GUIDE.md) 了解如何使用

