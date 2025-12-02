# VideoLingo 前端重构与推进计划

## 一、 现有代码分析 (Current Status Analysis)

### 1. 项目架构
- **技术栈**: Electron + Vue 3 + Vite + Pinia + TypeScript。
- **目录结构**: 结构清晰，分层合理 (`pages`, `components`, `store`, `api`, `layouts`)。
- **路由**: `router/index.ts` 基本符合设计文档，但部分页面仍使用占位符 (`Tasks.vue`, `Downloads.vue` 复用)。

### 2. 核心组件分析
- **`Player.vue` (视频学习页)**:
  - **问题**: 代码过于庞大 (Monolithic)。集成了视频播放控制、字幕渲染、Tab 切换逻辑、以及大量的 Whisper 模拟数据处理逻辑。
  - **耦合**: UI 逻辑与数据处理逻辑（模拟的提取、翻译、标注）高度耦合，难以维护和扩展。
- **`Home.vue` (首页)**:
  - **问题**: 数据主要为硬编码 (Hardcoded)，未真正连接到 Store 或持久化数据。
- **`Videos.vue` (视频列表)**:
  - **问题**: 依赖 `window.api` 进行文件操作，逻辑尚可，但缺乏对视频元数据的持久化存储机制（目前仅在 Store 内存中）。

### 3. 数据处理 (Data Processing)
- **现状**: `api/whisper.ts` 定义了与 Python 后端的接口，但 `Player.vue` 中使用了大量的 "MOCK FLOW" 代码来模拟进度和加载示例文件。
- **问题**: 真实的业务逻辑（提取 -> 翻译 -> 标注）散落在 UI 组件中。缺乏一个统一的服务层来管理这些耗时任务的状态。

### 4. UI/设计 (UI/Design)
- **现状**: 目前使用了深色主题 (`#020617` 背景，蓝紫色渐变)，偏向 "极客/Cyberpunk" 风格。
- **问题**: `design_reference.md` 明确建议 "轻量教育工具风" (Light Theme, e.g., `#F5F5F5`)。现有风格与需求不符，且深色高对比度可能不适合长时间的语言学习阅读。

---

## 二、 重构与推进计划 (Refactoring Plan)

### 阶段一：组件解耦与重构 (Frontend Refactoring)
**目标**: 拆分 `Player.vue`，降低复杂度。

1.  **拆分 `Player.vue`**:
    -   `VideoPlayer.vue`: 专注视频播放、时间轴控制、底部字幕渲染。
    -   `PlayerSidebar.vue`: 管理右侧 Tabs 容器。
    -   `TabSubtitles.vue`: 滚动字幕列表。
    -   `TabWords.vue`: 单词/词汇表。
    -   `TabNotes.vue`: 笔记功能。
2.  **优化 Store**:
    -   确保 `videos`, `subtitles`, `notes` 等 Store 能够正确响应数据变化。

### 阶段二：数据处理服务化 (Data Processing Layer)
**目标**: 将 Whisper 处理逻辑从 UI 中剥离。

1.  **创建 `services/taskManager.ts`**:
    -   统一管理 "提取"、"翻译"、"标注" 等异步任务。
    -   处理 模拟 (Mock) vs 真实 (Real) 的切换逻辑。在开发环境或未连接后端时优雅降级。
    -   管理任务状态 (Idle, Processing, Completed, Error) 和进度。
2.  **集成 Python 后端 (初步)**:
    -   虽然暂不深入后端开发，但前端需建立标准的轮询 (Polling) 或 WebSocket 机制来获取任务状态，替换掉 `Player.vue` 中的 `setTimeout` 模拟。

### 阶段三：UI/UX 改进 (UI Redesign)
**目标**: 实现 "轻量教育工具风"。

1.  **主题切换**:
    -   引入 CSS 变量系统 (Variables)，支持 Light/Dark 模式切换。
    -   **默认 Light Mode**:
        -   背景: `#F8FAFC` (Slate-50) 或 `#FFFFFF`。
        -   卡片: `#FFFFFF` + 轻微阴影。
        -   主色: `#2563EB` (Blue-600) 保持不变，作为强调色。
        -   文字: `#1E293B` (Slate-800) 用于正文，保证阅读舒适度。
2.  **细节优化**:
    -   去除过多的渐变背景，使用纯色或极淡的纹理。
    -   优化排版间距，增加呼吸感。

---

## 三、 美术/UI 改进建议 (Art/UI Suggestions)

针对 "不喜欢很多细节" 的反馈，建议如下：

1.  **去噪**: 移除 `AppLayout.vue` 和 `theme.css` 中的复杂 `radial-gradient` 背景。教育软件应保持背景干净，避免干扰注意力。
2.  **扁平化**: 减少卡片的强阴影和边框，使用更柔和的分割线或背景色差来区分区块。
3.  **字体**: 确保中英文混排的舒适度，增大正文字号 (14px -> 15px/16px)，增加行高。
4.  **图标**: 使用一套风格统一的线性图标 (如 Heroicons Outline 或 Phosphor Icons)，避免 emoji 混用。

---

## 四、 执行步骤 (Action Items)

1.  [ ] **重构 Player**: 创建 `src/renderer/pages/player/` 目录，拆分组件。
2.  [ ] **建立 Service**: 创建 `src/renderer/services/`，迁移 Whisper 逻辑。
3.  [ ] **样式调整**: 修改 `theme.css`，定义 Light Theme 变量，去除深色渐变。
4.  [ ] **数据持久化**: 引入 `pinia-plugin-persistedstate` 确保刷新后数据不丢失。
