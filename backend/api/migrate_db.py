"""
数据库迁移脚本
用于更新现有数据库，添加 is_admin 字段和 audit_logs 表
"""
import sqlite3
from pathlib import Path

def migrate_database():
    db_path = Path(__file__).parent / "videolingo.db"

    print(f"正在迁移数据库: {db_path}")

    if not db_path.exists():
        print("数据库文件不存在，将在首次运行时自动创建")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查 users 表是否已有 is_admin 字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'is_admin' not in columns:
            print("添加 is_admin 字段到 users 表...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
            print("✓ is_admin 字段添加成功")
        else:
            print("✓ is_admin 字段已存在")

        # 检查 audit_logs 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_logs'")
        if not cursor.fetchone():
            print("创建 audit_logs 表...")
            cursor.execute("""
                CREATE TABLE audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action VARCHAR NOT NULL,
                    operator_id INTEGER NOT NULL,
                    target_user_id INTEGER,
                    reason TEXT,
                    details JSON,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY(operator_id) REFERENCES users(id)
                )
            """)
            cursor.execute("CREATE INDEX ix_audit_logs_id ON audit_logs (id)")
            cursor.execute("CREATE INDEX ix_audit_logs_action ON audit_logs (action)")
            cursor.execute("CREATE INDEX ix_audit_logs_created_at ON audit_logs (created_at)")
            print("✓ audit_logs 表创建成功")
        else:
            print("✓ audit_logs 表已存在")

        conn.commit()
        print("\n数据库迁移完成！")

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
