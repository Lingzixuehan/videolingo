"""
设置用户为管理员的辅助脚本
"""
import sqlite3
import sys
from pathlib import Path

def set_admin(email: str):
    db_path = Path(__file__).parent / "videolingo.db"

    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 查找用户
        cursor.execute("SELECT id, email, is_admin FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            print(f"❌ 用户不存在: {email}")
            return

        user_id, user_email, is_admin = user

        if is_admin:
            print(f"✓ 用户 {user_email} (ID: {user_id}) 已经是管理员")
        else:
            # 设置为管理员
            cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
            conn.commit()
            print(f"✓ 用户 {user_email} (ID: {user_id}) 已设置为管理员")

    except Exception as e:
        print(f"❌ 操作失败: {e}")
    finally:
        conn.close()

def list_users():
    db_path = Path(__file__).parent / "videolingo.db"

    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, email, is_admin, created_at FROM users")
        users = cursor.fetchall()

        if not users:
            print("没有用户")
            return

        print("\n用户列表:")
        print("-" * 80)
        print(f"{'ID':<5} {'邮箱':<30} {'管理员':<10} {'创建时间':<25}")
        print("-" * 80)
        for user in users:
            user_id, email, is_admin, created_at = user
            admin_str = "是" if is_admin else "否"
            print(f"{user_id:<5} {email:<30} {admin_str:<10} {created_at:<25}")
        print("-" * 80)

    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  设置管理员: python set_admin.py <email>")
        print("  列出用户:   python set_admin.py --list")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_users()
    else:
        email = sys.argv[1]
        set_admin(email)
