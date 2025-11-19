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
```bash
app/
  api/        # auth.py / health.py / root.py
  core/       # config.py / security.py（JWT & 密码哈希）
  db/         # session.py（engine / SessionLocal / Base / get_db）
  models/     # user.py / card.py / review.py
  schemas/    # Pydantic v2 模型
  main.py     # FastAPI 入口 & 路由挂载
alembic/      # 迁移脚本目录（init 后生成）
alembic.ini   # Alembic 配置
pytest.ini    # pythonpath=.
requirements.txt / requirements-dev.txt
ruff.toml / mypy.ini
.env.example
```
## 环境变量（.env）

``` bash
ENV=dev
PORT=8000
VERSION=0.1.0

DATABASE_URL=sqlite:///./videolingo.db
SECRET_KEY=change-me         # 生产环境请改为强随机
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

```
## 表模型
``` bash
users 1 ────< cards 1 ────< reviews
```
users：id, email(唯一), hashed_password, created_at

cards（卡片 + 调度）：user_id, front, back, deck, tags(JSON), extras(JSON), state, due_at, interval, ease_factor, reps, lapses, created_at, updated_at, deleted_at

reviews（复习/审计日志）：user_id, card_id, rating(0~3), sched_before(JSON), sched_after(JSON), reviewed_at

说明：tags/extras 为扩展字段；SRS 调度字段用于“今天到期卡片”的筛选与复习后写回。

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
## 迁移（Alembic）

安装 & 初始化（首次）
已写入 requirements-dev.txt，安装后执行：
```
# 推荐使用模块方式，避免 PATH 问题
python -m alembic --version
python -m alembic init alembic
```
我们在 alembic/env.py 中从 app.core.config.settings.DATABASE_URL 注入连接串；alembic.ini 的 sqlalchemy.url 留空即可。


生成迁移脚本
```
# 根据模型差异自动生成
python -m alembic revision -m "init users/cards/reviews" --autogenerate

```
生成的脚本位于 alembic/versions/，包含 upgrade()/downgrade()。务必打开检查，必要时手工调整（尤其 SQLite 的列变更）。


执行迁移 / 回滚
```
# 升级到最新
python -m alembic upgrade head
# 回退一个版本
python -m alembic downgrade -1

```
开发阶段可以保留 Base.metadata.create_all() 仅在 ENV=dev 时执行；生产/CI 以 Alembic 迁移为准。

迁移速查：加一列示例
```
python -m alembic revision -m "add difficulty to cards"
# 打开生成脚本，填入：
# upgrade(): op.add_column("cards", sa.Column("difficulty", sa.Float(), server_default="1.0", nullable=False)); op.alter_column("cards","difficulty", server_default=None)
# downgrade(): op.drop_column("cards", "difficulty")
python -m alembic upgrade head

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

## API 快速验证
```
# 健康
curl http://127.0.0.1:8000/health

# 注册
curl -X POST http://127.0.0.1:8000/register -H "Content-Type: application/json" \
  -d "{\"email\":\"u1@example.com\",\"password\":\"secret123\"}"

# 登录 → token
curl -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" \
  -d "{\"email\":\"u1@example.com\",\"password\":\"secret123\"}"

# 受保护接口
curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer <JWT>"

```