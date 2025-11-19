from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings
from app.core.security import verify_token
from app.db import session as db_session
from app.main import app
import uuid

client = TestClient(app)


def test_register_duplicate_and_short_password():
    # 用随机邮箱避免与其它测试冲突
    email1 = f"u{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/register", json={"email": email1, "password": "secret123"})
    assert r.status_code == 200

    # 重复邮箱 → 400（覆盖 auth.py:29）
    r2 = client.post("/register", json={"email": email1, "password": "secret123"})
    assert r2.status_code == 400

    # 短密码 → 400（覆盖 auth.py:36/38）
    email2 = f"u{uuid.uuid4().hex[:8]}@example.com"
    r3 = client.post("/register", json={"email": email2, "password": "123"})
    assert r3.status_code == 400


def test_login_wrong_password_triggers_branch():
    client.post("/register", json={"email": "u3@example.com", "password": "secret123"})
    # 错误密码 → 401（覆盖 auth.py:51）
    r = client.post("/login", json={"email": "u3@example.com", "password": "wrong"})
    assert r.status_code == 401


def test_verify_token_error_branches():
    # 缺少 sub → 401（覆盖 security.py:36/37）
    t_no_sub = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(seconds=60)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(HTTPException):
        verify_token(t_no_sub)

    # 错误签名/或过期 → 401（覆盖 security.py:34）
    t_bad_sig = jwt.encode(
        {"sub": "x@example.com", "exp": datetime.now(timezone.utc) + timedelta(seconds=60)},
        "wrong-secret",
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(HTTPException):
        verify_token(t_bad_sig)


def test_get_db_closes_session(monkeypatch):
    closed = {"ok": False}

    class Dummy:
        def close(self):
            closed["ok"] = True

    monkeypatch.setattr(db_session, "SessionLocal", lambda: Dummy())
    gen = db_session.get_db()
    _ = next(gen)  # 进入生成器
    with pytest.raises(StopIteration):
        next(gen)  # 推进到 finally
    assert closed["ok"] is True  # 覆盖 session.py:14–18
