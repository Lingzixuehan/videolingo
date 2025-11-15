# Videolingo 卡片同步 API 文档

## 概述

这是 Videolingo 项目的卡片同步 API，支持用户在学习视频时创建、查询、更新和删除学习卡片。所有卡片操作都需要用户进行身份认证。

## API 端点概览

| 方法 | 端点 | 描述 |
|-----|------|------|
| `POST` | `/register` | 用户注册 |
| `POST` | `/login` | 用户登录 |
| `GET` | `/users/me` | 获取当前用户信息 |
| `POST` | `/cards` | 上传/创建卡片 |
| `GET` | `/cards` | 查询卡片列表（支持多种过滤条件） |
| `GET` | `/cards/{id}` | 获取单个卡片 |
| `PUT` | `/cards/{id}` | 更新卡片 |
| `DELETE` | `/cards/{id}` | 删除卡片 |

---

## 认证

所有卡片操作都需要通过 JWT Token 认证。

### 1. 用户注册

**端点**: `POST /register`

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com"
}
```

### 2. 用户登录

**端点**: `POST /login`

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**使用 Token 进行请求**:
```
Authorization: Bearer <access_token>
```

---

## 卡片 API 端点

### 1. 上传卡片

**端点**: `POST /cards`

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "video_id": "video_001",
  "timestamp": 123.45,
  "tags": "Python,API",
  "content": {
    "title": "卡片标题",
    "description": "卡片描述",
    "note": "自定义笔记内容",
    "any_key": "any_value"
  }
}
```

**参数说明**:
- `video_id` (string, 必需): 视频的唯一标识符
- `timestamp` (float, 可选): 视频中的时间戳（秒）
- `tags` (string, 可选): 标签，多个标签用逗号分隔
- `content` (object, 必需): JSON 格式的卡片内容，可包含任意字段

**响应** (200 OK):
```json
{
  "id": 1,
  "video_id": "video_001",
  "timestamp": 123.45,
  "tags": "Python,API",
  "content": {
    "title": "卡片标题",
    "description": "卡片描述",
    "note": "自定义笔记内容",
    "any_key": "any_value"
  },
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

---

### 2. 查询卡片列表

**端点**: `GET /cards`

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
| 参数 | 类型 | 说明 |
|-----|------|------|
| `video_id` | string | 按视频ID筛选 |
| `timestamp_from` | float | 时间戳范围下限 |
| `timestamp_to` | float | 时间戳范围上限 |
| `tags` | string | 按标签模糊匹配 |
| `skip` | integer | 跳过的记录数（分页） |
| `limit` | integer | 返回的最大记录数（默认100） |

**示例请求**:
```
GET /cards?video_id=video_001&timestamp_from=100&timestamp_to=200&skip=0&limit=10
```

**响应** (200 OK):
```json
{
  "cards": [
    {
      "id": 1,
      "video_id": "video_001",
      "timestamp": 123.45,
      "tags": "Python,API",
      "content": {...},
      "created_at": "2025-01-15T10:30:00",
      "updated_at": "2025-01-15T10:30:00"
    },
    {
      "id": 2,
      "video_id": "video_001",
      "timestamp": 150.00,
      "tags": "API,Learning",
      "content": {...},
      "created_at": "2025-01-15T10:35:00",
      "updated_at": "2025-01-15T10:35:00"
    }
  ],
  "total": 2
}
```

**查询示例**:

1. **按视频ID查询**:
   ```
   GET /cards?video_id=video_001
   ```

2. **按时间戳范围查询**:
   ```
   GET /cards?timestamp_from=100.0&timestamp_to=500.0
   ```

3. **按标签查询**:
   ```
   GET /cards?tags=API
   ```

4. **组合查询**:
   ```
   GET /cards?video_id=video_001&tags=Python&skip=0&limit=20
   ```

---

### 3. 获取单个卡片

**端点**: `GET /cards/{id}`

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id` (integer): 卡片ID

**响应** (200 OK):
```json
{
  "id": 1,
  "video_id": "video_001",
  "timestamp": 123.45,
  "tags": "Python,API",
  "content": {...},
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

**错误响应** (404 Not Found):
```json
{
  "detail": "卡片不存在"
}
```

---

### 4. 更新卡片

**端点**: `PUT /cards/{id}`

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路径参数**:
- `id` (integer): 卡片ID

**请求体** (所有字段都是可选的):
```json
{
  "timestamp": 200.00,
  "tags": "Python,API,Updated",
  "content": {
    "title": "更新后的标题",
    "description": "更新后的描述"
  }
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "video_id": "video_001",
  "timestamp": 200.00,
  "tags": "Python,API,Updated",
  "content": {
    "title": "更新后的标题",
    "description": "更新后的描述"
  },
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T11:00:00"
}
```

---

### 5. 删除卡片

**端点**: `DELETE /cards/{id}`

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id` (integer): 卡片ID

**响应** (204 No Content):
```
(空响应体)
```

**错误响应** (404 Not Found):
```json
{
  "detail": "卡片不存在"
}
```

---

## 错误处理

### 常见错误代码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 204 | 删除成功（无响应体） |
| 400 | 请求参数错误 |
| 401 | 未授权（Token 无效或过期） |
| 404 | 资源不存在 |
| 422 | 请求验证失败 |
| 500 | 服务器内部错误 |

### 错误响应示例

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 使用示例

### Python 客户端示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 注册用户
register_data = {
    "email": "user@example.com",
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/register", json=register_data)
print(response.json())

# 2. 登录获取 Token
login_data = {
    "email": "user@example.com",
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/login", json=login_data)
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 3. 上传卡片
card_data = {
    "video_id": "video_001",
    "timestamp": 123.45,
    "tags": "Python,API",
    "content": {
        "title": "学习笔记",
        "description": "关于 API 的笔记"
    }
}
response = requests.post(f"{BASE_URL}/cards", json=card_data, headers=headers)
card = response.json()
print(f"卡片已创建，ID: {card['id']}")

# 4. 查询卡片
response = requests.get(f"{BASE_URL}/cards?video_id=video_001", headers=headers)
cards = response.json()
print(f"找到 {cards['total']} 张卡片")

# 5. 更新卡片
update_data = {
    "tags": "Python,API,Updated",
    "content": {"title": "更新的笔记"}
}
response = requests.put(f"{BASE_URL}/cards/{card['id']}", json=update_data, headers=headers)
print(response.json())

# 6. 删除卡片
response = requests.delete(f"{BASE_URL}/cards/{card['id']}", headers=headers)
print(f"卡片已删除")
```

### JavaScript/TypeScript 客户端示例

```javascript
const BASE_URL = "http://localhost:8000";

// 1. 登录获取 Token
async function login() {
  const response = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "user@example.com",
      password: "password123"
    })
  });
  return await response.json();
}

// 2. 上传卡片
async function createCard(token, cardData) {
  const response = await fetch(`${BASE_URL}/cards`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(cardData)
  });
  return await response.json();
}

// 3. 查询卡片
async function getCards(token, filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(
    `${BASE_URL}/cards?${params}`,
    {
      headers: { "Authorization": `Bearer ${token}` }
    }
  );
  return await response.json();
}

// 4. 更新卡片
async function updateCard(token, cardId, updates) {
  const response = await fetch(`${BASE_URL}/cards/${cardId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(updates)
  });
  return await response.json();
}

// 5. 删除卡片
async function deleteCard(token, cardId) {
  const response = await fetch(`${BASE_URL}/cards/${cardId}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${token}` }
  });
  return response.status === 204;
}

// 使用示例
(async () => {
  const { access_token } = await login();
  
  const card = await createCard(access_token, {
    video_id: "video_001",
    timestamp: 123.45,
    tags: "Python,API",
    content: { title: "学习笔记" }
  });
  
  const cards = await getCards(access_token, { video_id: "video_001" });
  console.log(`找到 ${cards.total} 张卡片`);
  
  await updateCard(access_token, card.id, { tags: "Python,API,Updated" });
  
  await deleteCard(access_token, card.id);
})();
```

---

## 运行和测试

### 安装依赖

```bash
pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib bcrypt python-multipart email-validator
```

### 启动服务器

```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动

### 运行测试脚本

```bash
python test_cards_api.py
```

测试脚本会自动执行以下操作：
- 注册新用户
- 登录获取 Token
- 创建多张卡片
- 测试各种查询条件
- 更新和删除卡片
- 测试错误情况

### 访问 API 文档

启动服务器后，可以通过以下 URL 访问自动生成的 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 数据库架构

### users 表

| 列名 | 类型 | 说明 |
|-----|------|------|
| id | INTEGER | 主键 |
| email | STRING | 邮箱（唯一） |
| hashed_password | STRING | 密码哈希值 |
| created_at | DATETIME | 创建时间 |

### cards 表

| 列名 | 类型 | 说明 |
|-----|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键，关联 users 表 |
| video_id | STRING | 视频ID（可索引） |
| timestamp | FLOAT | 时间戳（可索引） |
| tags | STRING | 标签（可索引） |
| content | JSON | JSON 格式内容 |
| created_at | DATETIME | 创建时间（可索引） |
| updated_at | DATETIME | 更新时间 |

---

## 安全注意事项

1. **生产环境**: 更改 `auth.py` 中的 `SECRET_KEY` 为强密钥
2. **HTTPS**: 生产环境必须使用 HTTPS
3. **Token 过期**: 设置合理的 Token 过期时间
4. **CORS**: 根据需要配置跨域资源共享
5. **速率限制**: 考虑添加 API 速率限制
6. **验证**: 所有输入都应进行验证

---

## 常见问题

### Q: Token 过期了怎么办？
A: 需要重新调用 `/login` 接口获取新 Token。

### Q: 如何实现分页查询？
A: 使用 `skip` 和 `limit` 参数：
```
GET /cards?skip=0&limit=20
```

### Q: content 字段可以存储什么数据？
A: 任何有效的 JSON 数据，包括嵌套对象和数组。

### Q: 可以在没有 timestamp 的情况下创建卡片吗？
A: 可以，timestamp 是可选的。

---

## 许可证

该项目遵循相应的开源许可证。

