"""
卡片同步 API 测试脚本
测试所有卡片相关的接口：上传、查询、更新、删除
"""

import requests
import json
from typing import Dict, Any

# API 基础 URL
BASE_URL = "http://localhost:8000"

# 测试用户凭证
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"

# 全局变量：存储授权令牌
access_token = None

# HTTP 请求头
def get_headers():
    """获取包含授权信息的请求头"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

def print_result(title: str, response: requests.Response):
    """打印响应结果"""
    print(f"\n{'='*60}")
    print(f"测试: {title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应: {response.text}")

def test_register():
    """测试注册功能"""
    global access_token
    print(f"\n{'='*60}")
    print("测试: 用户注册")
    print(f"{'='*60}")
    
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    response = requests.post(f"{BASE_URL}/register", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✓ 注册成功")
    else:
        print("✗ 注册失败")

def test_login():
    """测试登录功能"""
    global access_token
    print(f"\n{'='*60}")
    print("测试: 用户登录")
    print(f"{'='*60}")
    
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"状态码: {response.status_code}")
    resp_json = response.json()
    print(f"响应: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        access_token = resp_json.get("access_token")
        print(f"✓ 登录成功，获取令牌: {access_token[:20]}...")
    else:
        print("✗ 登录失败")

def test_create_card() -> Dict[str, Any]:
    """测试上传卡片"""
    print(f"\n{'='*60}")
    print("测试: 上传卡片")
    print(f"{'='*60}")
    
    data = {
        "video_id": "video_001",
        "timestamp": 123.45,
        "tags": "Python,API",
        "content": {
            "title": "测试卡片",
            "description": "这是一个测试卡片",
            "note": "包含 JSON 格式的内容"
        }
    }
    response = requests.post(f"{BASE_URL}/cards", json=data, headers=get_headers())
    print_result("上传卡片", response)
    
    if response.status_code == 200:
        print("✓ 卡片上传成功")
        return response.json()
    else:
        print("✗ 卡片上传失败")
        return None

def test_list_cards_all():
    """测试查询所有卡片"""
    print(f"\n{'='*60}")
    print("测试: 查询所有卡片")
    print(f"{'='*60}")
    
    response = requests.get(f"{BASE_URL}/cards", headers=get_headers())
    print_result("查询所有卡片", response)
    
    if response.status_code == 200:
        print("✓ 查询成功")
        return response.json()
    else:
        print("✗ 查询失败")
        return None

def test_list_cards_by_video():
    """测试按视频ID查询卡片"""
    print(f"\n{'='*60}")
    print("测试: 按视频ID查询卡片")
    print(f"{'='*60}")
    
    params = {"video_id": "video_001"}
    response = requests.get(f"{BASE_URL}/cards", params=params, headers=get_headers())
    print_result("按视频ID查询", response)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 查询成功，找到 {result['total']} 张卡片")
    else:
        print("✗ 查询失败")

def test_list_cards_by_tags():
    """测试按标签查询卡片"""
    print(f"\n{'='*60}")
    print("测试: 按标签查询卡片")
    print(f"{'='*60}")
    
    params = {"tags": "API"}
    response = requests.get(f"{BASE_URL}/cards", params=params, headers=get_headers())
    print_result("按标签查询", response)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 查询成功，找到 {result['total']} 张卡片")
    else:
        print("✗ 查询失败")

def test_list_cards_by_timestamp():
    """测试按时间戳范围查询卡片"""
    print(f"\n{'='*60}")
    print("测试: 按时间戳范围查询卡片")
    print(f"{'='*60}")
    
    params = {"timestamp_from": 100.0, "timestamp_to": 200.0}
    response = requests.get(f"{BASE_URL}/cards", params=params, headers=get_headers())
    print_result("按时间戳范围查询", response)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 查询成功，找到 {result['total']} 张卡片")
    else:
        print("✗ 查询失败")

def test_get_card(card_id: int):
    """测试获取单个卡片"""
    print(f"\n{'='*60}")
    print(f"测试: 获取单个卡片 (ID: {card_id})")
    print(f"{'='*60}")
    
    response = requests.get(f"{BASE_URL}/cards/{card_id}", headers=get_headers())
    print_result(f"获取卡片 {card_id}", response)
    
    if response.status_code == 200:
        print("✓ 获取成功")
    else:
        print("✗ 获取失败")

def test_update_card(card_id: int):
    """测试更新卡片"""
    print(f"\n{'='*60}")
    print(f"测试: 更新卡片 (ID: {card_id})")
    print(f"{'='*60}")
    
    data = {
        "timestamp": 456.78,
        "tags": "Python,API,Updated",
        "content": {
            "title": "更新后的卡片",
            "description": "这是一个已更新的测试卡片",
            "note": "更新了 JSON 格式的内容"
        }
    }
    response = requests.put(f"{BASE_URL}/cards/{card_id}", json=data, headers=get_headers())
    print_result(f"更新卡片 {card_id}", response)
    
    if response.status_code == 200:
        print("✓ 更新成功")
    else:
        print("✗ 更新失败")

def test_delete_card(card_id: int):
    """测试删除卡片"""
    print(f"\n{'='*60}")
    print(f"测试: 删除卡片 (ID: {card_id})")
    print(f"{'='*60}")
    
    response = requests.delete(f"{BASE_URL}/cards/{card_id}", headers=get_headers())
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 204:
        print("✓ 删除成功")
    else:
        print("✗ 删除失败")
        print(f"响应: {response.text}")

def test_error_cases():
    """测试错误情况"""
    print(f"\n{'='*60}")
    print("测试: 错误情况")
    print(f"{'='*60}")
    
    # 不存在的卡片
    print("\n--- 测试获取不存在的卡片 ---")
    response = requests.get(f"{BASE_URL}/cards/99999", headers=get_headers())
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 404:
        print("✓ 正确返回 404")
    
    # 无效的请求体
    print("\n--- 测试无效的请求体 ---")
    data = {"video_id": "test"}  # 缺少 content 字段
    response = requests.post(f"{BASE_URL}/cards", json=data, headers=get_headers())
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 422:
        print("✓ 正确返回 422 验证错误")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始执行卡片同步 API 测试")
    print("="*60)
    
    # 注册和登录
    test_register()
    test_login()
    
    if not access_token:
        print("\n✗ 无法获取授权令牌，停止测试")
        return
    
    # 创建卡片
    card1 = test_create_card()
    
    # 创建多张卡片以便测试查询
    print(f"\n{'='*60}")
    print("创建更多测试卡片...")
    print(f"{'='*60}")
    
    for i in range(2, 4):
        data = {
            "video_id": f"video_{i:03d}" if i % 2 == 0 else "video_001",
            "timestamp": 100.0 + i * 50,
            "tags": "Test,Python" if i % 2 == 0 else "API,Learning",
            "content": {"text": f"卡片 {i}"}
        }
        response = requests.post(f"{BASE_URL}/cards", json=data, headers=get_headers())
        if response.status_code == 200:
            print(f"✓ 卡片 {i} 创建成功 (ID: {response.json()['id']})")
    
    # 查询测试
    list_result = test_list_cards_all()
    test_list_cards_by_video()
    test_list_cards_by_tags()
    test_list_cards_by_timestamp()
    
    # 单个卡片操作
    if card1:
        card_id = card1["id"]
        test_get_card(card_id)
        test_update_card(card_id)
        test_get_card(card_id)  # 验证更新
        test_delete_card(card_id)
        test_get_card(card_id)  # 应该返回 404
    
    # 错误情况测试
    test_error_cases()
    
    print(f"\n{'='*60}")
    print("所有测试完成!")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
