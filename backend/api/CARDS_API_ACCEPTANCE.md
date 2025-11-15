# 卡片同步 API - 需求验收清单

## 项目需求

**描述**: 实现 /cards 上传、/cards?filter 拉取、/cards/{id} 删除/更新

**验收标准**: 客户端能上传 JSON 并能按视频/时间戳/标签查询

---

## 功能实现清单

### ✅ 1. 卡片数据库模型 (models.py)

- [x] 创建 `Card` 数据库模型
- [x] 字段包括：
  - `id` - 主键
  - `user_id` - 外键关联用户
  - `video_id` - 视频ID（可索引）
  - `timestamp` - 时间戳（可索引）
  - `tags` - 标签（可索引）
  - `content` - JSON 内容
  - `created_at` - 创建时间
  - `updated_at` - 更新时间
- [x] 建立 User 和 Card 的关系

### ✅ 2. 数据验证模型 (schemas.py)

- [x] `CardCreate` - 卡片创建请求模型
- [x] `CardUpdate` - 卡片更新请求模型
- [x] `CardResponse` - 卡片响应模型
- [x] `CardListResponse` - 卡片列表响应模型

### ✅ 3. API 端点实现 (main.py)

#### 3.1 上传卡片
- [x] `POST /cards` 端点
- [x] 创建新卡片
- [x] 将卡片关联到当前用户
- [x] 返回创建的卡片信息
- [x] 支持上传 JSON 格式的 content

#### 3.2 查询卡片列表
- [x] `GET /cards` 端点
- [x] 支持按 `video_id` 筛选
- [x] 支持按 `timestamp_from` 和 `timestamp_to` 筛选
- [x] 支持按 `tags` 模糊查询
- [x] 支持分页（`skip` 和 `limit`）
- [x] 返回卡片列表和总数
- [x] 只返回当前用户的卡片

#### 3.3 获取单个卡片
- [x] `GET /cards/{id}` 端点
- [x] 获取指定 ID 的卡片
- [x] 验证卡片属于当前用户
- [x] 不存在时返回 404

#### 3.4 更新卡片
- [x] `PUT /cards/{id}` 端点
- [x] 支持更新 `timestamp`、`tags`、`content`
- [x] 验证卡片属于当前用户
- [x] 更新 `updated_at` 字段
- [x] 返回更新后的卡片信息

#### 3.5 删除卡片
- [x] `DELETE /cards/{id}` 端点
- [x] 删除指定 ID 的卡片
- [x] 验证卡片属于当前用户
- [x] 返回 204 No Content
- [x] 不存在时返回 404

### ✅ 4. 认证和授权

- [x] 所有卡片操作都需要 Bearer Token 认证
- [x] 用户只能访问自己的卡片
- [x] Token 验证正常工作

### ✅ 5. 错误处理

- [x] 非法请求返回 422 验证错误
- [x] 未授权请求返回 401
- [x] 资源不存在返回 404
- [x] 参数错误返回 400

### ✅ 6. 测试和文档

- [x] 编写详细的 API 文档 (CARDS_API_DOCS.md)
- [x] 创建完整的测试脚本 (test_cards_api.py)
- [x] 测试脚本包含：
  - 注册和登录
  - 创建多张卡片
  - 各种查询场景
  - 更新和删除操作
  - 错误情况处理

---

## 验收测试

### 测试场景

#### 1. 上传 JSON 卡片
```
POST /cards
{
  "video_id": "video_001",
  "timestamp": 123.45,
  "tags": "Python,API",
  "content": {
    "title": "测试卡片",
    "description": "JSON内容"
  }
}

预期结果: 200 OK，返回卡片信息 ✓
```

#### 2. 按视频ID查询
```
GET /cards?video_id=video_001

预期结果: 200 OK，返回该视频的所有卡片 ✓
```

#### 3. 按时间戳范围查询
```
GET /cards?timestamp_from=100.0&timestamp_to=500.0

预期结果: 200 OK，返回时间戳在范围内的卡片 ✓
```

#### 4. 按标签查询
```
GET /cards?tags=API

预期结果: 200 OK，返回标签包含 "API" 的卡片 ✓
```

#### 5. 组合查询
```
GET /cards?video_id=video_001&tags=Python&skip=0&limit=10

预期结果: 200 OK，返回符合所有条件的卡片 ✓
```

#### 6. 获取单个卡片
```
GET /cards/1

预期结果: 200 OK，返回ID为1的卡片 ✓
```

#### 7. 更新卡片
```
PUT /cards/1
{
  "tags": "Python,API,Updated",
  "content": {"title": "更新的内容"}
}

预期结果: 200 OK，返回更新后的卡片 ✓
```

#### 8. 删除卡片
```
DELETE /cards/1

预期结果: 204 No Content ✓
```

#### 9. 未授权访问
```
GET /cards (无Token)

预期结果: 401 Unauthorized ✓
```

#### 10. 不存在的卡片
```
GET /cards/99999

预期结果: 404 Not Found ✓
```

---

## 项目文件结构

```
e:\videolingo\
├── auth.py                    # 认证模块
├── database.py                # 数据库配置
├── main.py                    # 主应用（包含所有API端点）
├── models.py                  # 数据库模型
├── schemas.py                 # 数据验证模型
├── requirements.txt           # 依赖列表
├── CARDS_API_DOCS.md         # API文档
├── test_cards_api.py         # 测试脚本
└── videolingo.db             # SQLite数据库（运行时生成）
```

---

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLite（SQLAlchemy ORM）
- **认证**: JWT + Bearer Token
- **密码加密**: bcrypt
- **数据验证**: Pydantic
- **HTTP客户端**: requests（测试用）

---

## API 速览表

| 操作 | 方法 | 端点 | 认证 | 描述 |
|-----|------|------|------|------|
| 创建 | POST | `/cards` | ✓ | 上传新卡片 |
| 读取列表 | GET | `/cards` | ✓ | 查询卡片（可过滤） |
| 读取单个 | GET | `/cards/{id}` | ✓ | 获取单个卡片 |
| 更新 | PUT | `/cards/{id}` | ✓ | 修改卡片信息 |
| 删除 | DELETE | `/cards/{id}` | ✓ | 删除卡片 |

---

## 支持的查询过滤

| 参数 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| `video_id` | string | 按视频ID | `?video_id=video_001` |
| `timestamp_from` | float | 时间戳下限 | `?timestamp_from=100.0` |
| `timestamp_to` | float | 时间戳上限 | `?timestamp_to=500.0` |
| `tags` | string | 标签模糊匹配 | `?tags=Python` |
| `skip` | int | 跳过数量 | `?skip=0` |
| `limit` | int | 返回数量 | `?limit=20` |

---

## 需求验收总结

| 需求项 | 状态 | 说明 |
|--------|------|------|
| 上传卡片 | ✅ 完成 | POST /cards 端点实现，支持JSON上传 |
| 拉取卡片列表 | ✅ 完成 | GET /cards 端点实现，支持多种过滤 |
| 删除卡片 | ✅ 完成 | DELETE /cards/{id} 端点实现 |
| 更新卡片 | ✅ 完成 | PUT /cards/{id} 端点实现 |
| 按视频查询 | ✅ 完成 | 支持 video_id 参数 |
| 按时间戳查询 | ✅ 完成 | 支持 timestamp_from/to 参数 |
| 按标签查询 | ✅ 完成 | 支持 tags 参数（模糊匹配） |
| JSON内容存储 | ✅ 完成 | content 字段为 JSON 类型 |
| 认证保护 | ✅ 完成 | 所有操作都需要有效的 Token |
| 文档完善 | ✅ 完成 | 包含详细的 API 文档和使用示例 |

---

## 部署说明

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
python main.py
```

### 3. 运行测试
```bash
python test_cards_api.py
```

### 4. 访问 API 文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 后续改进建议

1. **缓存优化**: 为热点查询添加 Redis 缓存
2. **批量操作**: 支持批量创建、更新、删除卡片
3. **搜索功能**: 增强全文搜索能力
4. **版本控制**: 实现卡片版本历史
5. **分享功能**: 支持卡片分享和协作
6. **导出功能**: 支持导出为 CSV/PDF
7. **WebSocket**: 实时卡片同步
8. **速率限制**: 防止 API 滥用

