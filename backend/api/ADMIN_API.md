# 管理员删除用户 + 审计日志功能文档

## 功能概述

实现了管理员级别的用户删除接口，并在审计日志表中记录所有删除操作。

### 主要特性

- ✅ 管理员权限验证
- ✅ 删除用户及其关联数据（卡片）
- ✅ 不返回敏感信息（邮箱/密码）
- ✅ 完整的审计日志记录
- ✅ 审计日志查询接口（支持多种筛选条件）

## 数据库变更

### User 表新增字段

```sql
is_admin BOOLEAN NOT NULL DEFAULT 0  -- 是否为管理员
```

### 新增 AuditLog 表

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    action VARCHAR NOT NULL,              -- 操作类型（如 'delete_user'）
    operator_id INTEGER NOT NULL,         -- 操作人ID
    target_user_id INTEGER,               -- 被操作的用户ID
    reason TEXT,                          -- 操作理由
    details JSON,                         -- 额外详情（JSON格式）
    created_at DATETIME NOT NULL,         -- 创建时间
    FOREIGN KEY(operator_id) REFERENCES users(id)
)
```

## API 接口

### 1. 管理员删除用户

**接口**: `DELETE /admin/users/{user_id}`

**权限**: 需要管理员权限

**请求头**:
```
Authorization: Bearer <admin_token>
```

**请求体**:
```json
{
  "reason": "违反平台规定"
}
```

**响应** (200 OK):
```json
{
  "message": "用户删除成功",
  "deleted_user_id": 123,
  "audit_log_id": 45
}
```

**错误响应**:
- `401 Unauthorized`: 未登录或 token 无效
- `403 Forbidden`: 不是管理员
- `404 Not Found`: 用户不存在
- `400 Bad Request`: 尝试删除自己

### 2. 查询审计日志

**接口**: `GET /admin/audit-logs`

**权限**: 需要管理员权限

**请求头**:
```
Authorization: Bearer <admin_token>
```

**查询参数**:
- `action` (可选): 操作类型筛选，如 "delete_user"
- `operator_id` (可选): 操作人ID筛选
- `target_user_id` (可选): 被操作用户ID筛选
- `skip` (可选): 分页偏移，默认 0
- `limit` (可选): 每页数量，默认 100

**响应** (200 OK):
```json
{
  "logs": [
    {
      "id": 1,
      "action": "delete_user",
      "operator_id": 1,
      "target_user_id": 123,
      "reason": "违反平台规定",
      "details": {
        "operator_email": "admin@test.com",
        "deleted_user_id": 123
      },
      "created_at": "2025-12-04T10:30:00"
    }
  ],
  "total": 1
}
```

**错误响应**:
- `401 Unauthorized`: 未登录或 token 无效
- `403 Forbidden`: 不是管理员

## 使用指南

### 1. 数据库迁移

如果是现有数据库，运行迁移脚本：

```bash
cd backend/api
python migrate_db.py
```

### 2. 设置管理员

#### 方法1：使用辅助脚本

```bash
# 查看所有用户
python set_admin.py --list

# 设置指定用户为管理员
python set_admin.py admin@test.com
```

#### 方法2：直接使用 SQL

```bash
sqlite3 videolingo.db "UPDATE users SET is_admin=1 WHERE email='admin@test.com'"
```

### 3. 测试功能

运行完整的测试脚本：

```bash
# 确保后端服务已启动
python main.py

# 在另一个终端运行测试
python test_admin_api.py
```

## 使用示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 管理员登录
response = requests.post(f"{BASE_URL}/login", json={
    "email": "admin@test.com",
    "password": "admin123"
})
admin_token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {admin_token}"}

# 2. 删除用户
delete_data = {
    "reason": "用户违反平台规定"
}
response = requests.delete(
    f"{BASE_URL}/admin/users/123",
    json=delete_data,
    headers=headers
)
print(response.json())

# 3. 查询审计日志
response = requests.get(
    f"{BASE_URL}/admin/audit-logs",
    headers=headers,
    params={"action": "delete_user", "limit": 10}
)
logs = response.json()
print(f"共有 {logs['total']} 条删除记录")
for log in logs["logs"]:
    print(f"用户 {log['target_user_id']} 被删除，理由: {log['reason']}")
```

### cURL 示例

```bash
# 1. 登录获取 token
TOKEN=$(curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}' | jq -r '.access_token')

# 2. 删除用户
curl -X DELETE http://localhost:8000/admin/users/123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason":"违反平台规定"}'

# 3. 查询审计日志
curl -X GET "http://localhost:8000/admin/audit-logs?action=delete_user" \
  -H "Authorization: Bearer $TOKEN"
```

## 审计日志字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 审计日志ID |
| `action` | String | 操作类型（如 "delete_user"） |
| `operator_id` | Integer | 操作人（管理员）的用户ID |
| `target_user_id` | Integer | 被操作的用户ID（对于删除操作） |
| `reason` | String | 操作理由（必填） |
| `details` | JSON | 额外详情（包含操作人邮箱等） |
| `created_at` | DateTime | 操作时间 |

## 安全考虑

1. **权限验证**: 所有管理员接口都经过双重验证（登录 + 管理员权限）
2. **隐私保护**: 删除响应不包含被删除用户的敏感信息
3. **防自删**: 管理员不能删除自己的账号
4. **完整审计**: 所有删除操作都记录在审计日志中
5. **级联删除**: 删除用户时自动删除其关联的卡片数据

## 文件清单

| 文件 | 说明 |
|------|------|
| `models.py` | 数据模型（User, Card, AuditLog） |
| `schemas.py` | API 数据验证模型 |
| `main.py` | API 路由和业务逻辑 |
| `migrate_db.py` | 数据库迁移脚本 |
| `set_admin.py` | 设置管理员权限的辅助脚本 |
| `test_admin_api.py` | 完整功能测试脚本 |
| `ADMIN_API.md` | 本文档 |

## 验收标准

✅ **已实现所有验收标准**：

1. ✅ 管理员可以删除用户
2. ✅ 删除响应不包含敏感信息（邮箱/密码）
3. ✅ 删除操作记录在 audit 表
4. ✅ 可以查询审计日志
5. ✅ 审计日志包含：操作人ID、被删除用户ID、时间、理由
6. ✅ 支持多种筛选条件查询审计日志

## 后续扩展建议

1. 添加软删除功能（标记删除而非真删除）
2. 添加批量删除接口
3. 添加审计日志导出功能（CSV/Excel）
4. 添加更多管理员操作的审计日志
5. 添加审计日志的搜索和高级筛选功能
