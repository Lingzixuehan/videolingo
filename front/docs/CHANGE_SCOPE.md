# Videolingo 客户端范围裁剪说明（Develop 分支）

本文仅适用于“客户端（Electron + Vue3）”。服务端与子服务的范围另行维护。

## 一、暂缓/不做（客户端）

- 讨论区全套功能（发帖、评论、审核、举报、分享）
- 平台字幕抓取（例如 YouTube 链接）
- 性能/系统资源监控可视化
- 第三方登录（微信/Google 等）
- 词汇量阈值高亮（改为词库来源标签展示）

## 二、保留/优先（客户端）

- 本地视频：导入/播放/删除；导入前合规确认；校验时长≤20min、大小≤500MB
- 字幕生成：前端触发本地 Whisper 子服务；结果本地落盘/缓存；字幕管理（选择/下载/编辑占位）
- 字幕展示：底部同步字幕（关/英/中/双语）；侧边滚动字幕；点击句子跳转
- 词汇/短语：点击字幕单词/短语弹出释义，展示 level_tag（如 CET4、CET6、TOEFL 等）
- 标注与收藏：在播放器中创建标注、收藏单词/短语/句子，并自动生成学习卡片
- 学习卡片：卡片列表管理、复习页面（简化间隔算法）；学习计划与桌面通知（本地）
- 数据：卡片/字幕/标注导出为 JSON；一键清除本地数据
- 认证：仅邮箱登录/注册/重置；客户端只显示用户名，不显示邮箱与密码；无用户信息修改入口

说明：
- 视频与字幕在“本地”处理与存储；学习卡片在“服务端”存储（客户端仅调用 API）。
- 前端配置通过 `.env` 注入 `VITE_API_BASE`，不得硬编码敏感信息。

## 三、客户端与后端接口边界（预期）

- Auth
  - `POST /api/auth/login`，`POST /api/auth/register`，`POST /api/auth/password-reset`
- Dict
  - `GET /api/dict/word/:word` → `{ word, phonetic?, pos?, meaning_cn, examples, level_tag }`
- Cards
  - `GET /api/cards`，`POST /api/cards`，`PATCH /api/cards/:id`，`DELETE /api/cards/:id`
  - `GET /api/cards/due`（到期复习列表），`POST /api/cards/:id/review`
- Videos/Subtitles
  - 客户端本地管理（选择/读取/渲染/导出）；如需服务端索引同步，另开议题

> 注：本文件作为客户端范围与需求真源，后续前端 issue 必须引用本文件。