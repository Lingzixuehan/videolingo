#!/bin/bash
# Videolingo 卡片同步 API - curl 命令示例
# 这个脚本包含了所有常见的 API 调用示例

BASE_URL="http://localhost:8000"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印标题
print_section() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

# 打印命令
print_command() {
    echo -e "${GREEN}$ $1${NC}"
}

# ====================
# 第一部分：认证
# ====================

print_section "1. 用户注册"
print_command "curl -X POST $BASE_URL/register -H 'Content-Type: application/json' -d '{\"email\":\"user@example.com\",\"password\":\"password123\"}'"

curl -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -w "\n"

# ====================

print_section "2. 用户登录"
print_command "curl -X POST $BASE_URL/login -H 'Content-Type: application/json' -d '{\"email\":\"user@example.com\",\"password\":\"password123\"}'"

# 登录并保存 token
TOKEN=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Error: 无法获取 token${NC}"
    exit 1
fi

# ====================
# 第二部分：卡片操作
# ====================

print_section "3. 获取当前用户信息"
print_command "curl -X GET $BASE_URL/users/me -H 'Authorization: Bearer <TOKEN>'"

curl -X GET "$BASE_URL/users/me" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\n"

# ====================

print_section "4. 上传第一张卡片"
print_command "curl -X POST $BASE_URL/cards -H 'Authorization: Bearer <TOKEN>' -H 'Content-Type: application/json' -d '{...}'"

CARD1=$(curl -s -X POST "$BASE_URL/cards" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "video_001",
    "timestamp": 123.45,
    "tags": "Python,API",
    "content": {
      "title": "测试卡片1",
      "description": "这是第一张测试卡片",
      "note": "包含 JSON 格式的内容"
    }
  }')

echo "$CARD1" | python -m json.tool

CARD1_ID=$(echo "$CARD1" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "Card 1 ID: $CARD1_ID"

# ====================

print_section "5. 上传第二张卡片"
print_command "curl -X POST $BASE_URL/cards -H 'Authorization: Bearer <TOKEN>' -H 'Content-Type: application/json' -d '{...}'"

CARD2=$(curl -s -X POST "$BASE_URL/cards" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "video_001",
    "timestamp": 200.00,
    "tags": "API,Learning",
    "content": {
      "title": "测试卡片2",
      "description": "这是第二张测试卡片",
      "note": "更多的 JSON 内容"
    }
  }')

echo "$CARD2" | python -m json.tool

CARD2_ID=$(echo "$CARD2" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "Card 2 ID: $CARD2_ID"

# ====================

print_section "6. 上传第三张卡片（不同视频）"
print_command "curl -X POST $BASE_URL/cards -H 'Authorization: Bearer <TOKEN>' -H 'Content-Type: application/json' -d '{...}'"

curl -s -X POST "$BASE_URL/cards" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "video_002",
    "timestamp": 150.00,
    "tags": "JavaScript",
    "content": {
      "title": "JavaScript 笔记",
      "description": "不同视频的卡片"
    }
  }' | python -m json.tool

# ====================

print_section "7. 查询所有卡片"
print_command "curl -X GET $BASE_URL/cards -H 'Authorization: Bearer <TOKEN>'"

curl -s -X GET "$BASE_URL/cards" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# ====================

print_section "8. 按视频 ID 查询"
print_command "curl -X GET '$BASE_URL/cards?video_id=video_001' -H 'Authorization: Bearer <TOKEN>'"

curl -s -X GET "$BASE_URL/cards?video_id=video_001" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# ====================

print_section "9. 按标签查询"
print_command "curl -X GET '$BASE_URL/cards?tags=API' -H 'Authorization: Bearer <TOKEN>'"

curl -s -X GET "$BASE_URL/cards?tags=API" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# ====================

print_section "10. 按时间戳范围查询"
print_command "curl -X GET '$BASE_URL/cards?timestamp_from=100&timestamp_to=250' -H 'Authorization: Bearer <TOKEN>'"

curl -s -X GET "$BASE_URL/cards?timestamp_from=100&timestamp_to=250" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# ====================

print_section "11. 分页查询"
print_command "curl -X GET '$BASE_URL/cards?skip=0&limit=2' -H 'Authorization: Bearer <TOKEN>'"

curl -s -X GET "$BASE_URL/cards?skip=0&limit=2" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# ====================

print_section "12. 获取单个卡片"
print_command "curl -X GET $BASE_URL/cards/$CARD1_ID -H 'Authorization: Bearer <TOKEN>'"

curl -s -X GET "$BASE_URL/cards/$CARD1_ID" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# ====================

print_section "13. 更新卡片"
print_command "curl -X PUT $BASE_URL/cards/$CARD1_ID -H 'Authorization: Bearer <TOKEN>' -H 'Content-Type: application/json' -d '{...}'"

curl -s -X PUT "$BASE_URL/cards/$CARD1_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": 130.00,
    "tags": "Python,API,Updated",
    "content": {
      "title": "更新后的卡片标题",
      "description": "这个卡片已被更新",
      "updated": true
    }
  }' | python -m json.tool

# ====================

print_section "14. 验证更新（再次获取卡片）"
print_command "curl -X GET $BASE_URL/cards/$CARD1_ID -H 'Authorization: Bearer <TOKEN>'"

curl -s -X GET "$BASE_URL/cards/$CARD1_ID" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# ====================

print_section "15. 删除卡片"
print_command "curl -X DELETE $BASE_URL/cards/$CARD2_ID -H 'Authorization: Bearer <TOKEN>'"

curl -s -X DELETE "$BASE_URL/cards/$CARD2_ID" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n${GREEN}✓ 卡片已删除${NC}\n"

# ====================

print_section "16. 验证删除（尝试获取已删除的卡片）"
print_command "curl -X GET $BASE_URL/cards/$CARD2_ID -H 'Authorization: Bearer <TOKEN>'"

curl -s -X GET "$BASE_URL/cards/$CARD2_ID" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# ====================

print_section "17. 测试错误情况 - 无效 Token"
print_command "curl -X GET $BASE_URL/cards -H 'Authorization: Bearer invalid_token'"

curl -s -X GET "$BASE_URL/cards" \
  -H "Authorization: Bearer invalid_token" | python -m json.tool

# ====================

print_section "18. 测试错误情况 - 缺少必需字段"
print_command "curl -X POST $BASE_URL/cards -H 'Authorization: Bearer <TOKEN>' -H 'Content-Type: application/json' -d '{\"video_id\":\"test\"}'"

curl -s -X POST "$BASE_URL/cards" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"video_id":"test"}' | python -m json.tool

# ====================

print_section "所有测试完成！"
echo -e "${GREEN}✓ curl 命令示例执行完毕${NC}"
