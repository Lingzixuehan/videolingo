"""
管理员删除用户和审计日志功能测试脚本
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_admin_features():
    print("=" * 60)
    print("管理员删除用户 + 审计日志 功能测试")
    print("=" * 60)

    # 1. 注册管理员用户
    print("\n1. 注册管理员用户...")
    admin_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/register", json=admin_data)
    if response.status_code == 200:
        print(f"✓ 管理员注册成功: {response.json()}")
        admin_user = response.json()
    else:
        print(f"✓ 管理员已存在（跳过注册）")

    # 2. 手动设置管理员权限（通过数据库）
    print("\n2. 设置管理员权限...")
    print("请手动运行以下 SQL 命令来设置管理员权限：")
    print("sqlite3 videolingo.db \"UPDATE users SET is_admin=1 WHERE email='admin@test.com'\"")
    input("设置完成后按回车继续...")

    # 3. 管理员登录
    print("\n3. 管理员登录...")
    response = requests.post(f"{BASE_URL}/login", json=admin_data)
    if response.status_code == 200:
        admin_token = response.json()["access_token"]
        print(f"✓ 登录成功，获取 token: {admin_token[:20]}...")
    else:
        print(f"❌ 登录失败: {response.json()}")
        return

    # 4. 注册普通用户
    print("\n4. 注册普通用户...")
    user_data = {
        "email": f"user_{datetime.now().timestamp()}@test.com",
        "password": "user123456"
    }
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    if response.status_code == 200:
        target_user = response.json()
        target_user_id = target_user["id"]
        print(f"✓ 用户注册成功，ID: {target_user_id}, Email: {target_user['email']}")
    else:
        print(f"❌ 注册失败: {response.json()}")
        return

    # 5. 测试非管理员删除用户（应该失败）
    print("\n5. 测试非管理员删除用户...")
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    if response.status_code == 200:
        user_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {user_token}"}
        delete_data = {"reason": "测试删除"}
        response = requests.delete(
            f"{BASE_URL}/admin/users/1",
            json=delete_data,
            headers=headers
        )
        if response.status_code == 403:
            print("✓ 正确拒绝非管理员删除请求")
        else:
            print(f"❌ 应该返回 403，实际返回: {response.status_code}")

    # 6. 管理员删除用户
    print("\n6. 管理员删除用户...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_data = {
        "reason": "测试删除用户功能 - 用户违反平台规定"
    }
    response = requests.delete(
        f"{BASE_URL}/admin/users/{target_user_id}",
        json=delete_data,
        headers=headers
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 删除成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
        audit_log_id = result.get("audit_log_id")
    else:
        print(f"❌ 删除失败 ({response.status_code}): {response.json()}")
        return

    # 7. 查询审计日志
    print("\n7. 查询审计日志...")
    response = requests.get(
        f"{BASE_URL}/admin/audit-logs",
        headers=headers,
        params={"action": "delete_user"}
    )
    if response.status_code == 200:
        logs = response.json()
        print(f"✓ 查询成功，共 {logs['total']} 条记录")
        for log in logs["logs"]:
            print(f"\n审计日志 #{log['id']}:")
            print(f"  - 操作: {log['action']}")
            print(f"  - 操作人ID: {log['operator_id']}")
            print(f"  - 被删除用户ID: {log['target_user_id']}")
            print(f"  - 理由: {log['reason']}")
            print(f"  - 时间: {log['created_at']}")
            print(f"  - 详情: {json.dumps(log['details'], ensure_ascii=False)}")
    else:
        print(f"❌ 查询失败 ({response.status_code}): {response.json()}")

    # 8. 验证用户已被删除
    print("\n8. 验证用户已被删除...")
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    if response.status_code == 401:
        print("✓ 用户已成功删除（登录失败）")
    else:
        print(f"❌ 用户似乎还存在")

    print("\n" + "=" * 60)
    print("✓ 所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_admin_features()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务已启动")
        print("运行: cd backend/api && python main.py")
