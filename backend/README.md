# Videolingo Backend (FastAPI) — GitLab CI ready

一个最小可用的 FastAPI 后端模板，内置 `GET /health` 健康检查、pytest 单测、Ruff+Mypy 代码检查、
以及 `.gitlab-ci.yml` 持续集成配置（可选 Docker 构建）。

## 本地运行

```bash
python -m venv .venv && source .venv/bin/activate  # Windows 用 .venv\Scripts\activate
pip install -U pip
pip install -r requirements-dev.txt
make run  # 或者: uvicorn app.main:app --reload
# 访问 http://127.0.0.1:8000/health
```

## 项目结构
backend/
├─ app/
│  ├─ core/
│  │  ├─ config.py           # Settings（.env 覆盖）
│  │  └─ security.py         # 密码哈希 & JWT
│  ├─ db/
│  │  ├─ __init__.py
│  │  └─ session.py          # engine / SessionLocal / Base / get_db
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ user.py             # SQLAlchemy User 模型
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  └─ user.py             # Pydantic v2 模型（from_attributes=True）
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ auth.py             # /register /login /users/me
│  │  ├─ health.py           # /health
│  │  └─ root.py             # /
│  └─ main.py                # FastAPI 入口 & include_router & 建表
├─ tests/
│  ├─ conftest.py            # 独立测试库、依赖覆盖
│  ├─ test_auth.py           # 注册/登录/鉴权流程
│  ├─ test_health.py
│  └─ test_root.py
├─ pytest.ini                # pythonpath = .
├─ requirements.txt
├─ requirements-dev.txt
├─ ruff.toml                 # 格式/规则（含 isort）
├─ mypy.ini
├─ .env.example
└─ (可选) Dockerfile

```

## 常用命令
```bash
make install     # 安装依赖（dev）
make run         # 本地启动 (localhost:8000)
make lint        # Ruff + Mypy
make test        # Pytest + 覆盖率
make format      # 代码格式化 (ruff format)
make docker-build
make docker-run
```

## 健康检查
- 访问 `GET /health` 将返回：`{"status":"ok","service":"videolingo-backend","version":"0.1.0"}`
- OpenAPI 文档：`/docs`

## 认证流程
```bash
# 注册
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"u1@example.com","password":"secret123"}'

# 登录 → 获取 token
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"u1@example.com","password":"secret123"}'
# {"access_token":"<JWT>","token_type":"bearer"}

# 带 token 访问受保护接口
curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer <JWT>"
```
## 测试 & 代码质量
``` bash
# 在 backend 目录 & 激活 venv
pytest -q --cov=app --cov-report=term-missing     # 单测 + 覆盖率
ruff check . --fix && ruff format .               # 规范 + 自动修复 & 格式化
mypy app                                          # 类型检查

```

## 部署建议
- 生产环境建议使用 Docker 运行：
  ```bash
  docker run -p 8000:8000 --env-file .env videolingo-backend:dev
  ```
- 或在云端/容器平台使用 `Dockerfile` 构建镜像部署。

## 安全与生产建议
SECRET_KEY 仅放环境变量或 .env；生产强制校验避免默认值：
``` bash
# app/main.py
from app.core.config import settings
if settings.ENV == "prod" and settings.SECRET_KEY == "change-me":
    raise RuntimeError("SECRET_KEY must be set in production")

```