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
```text
app/
  core/config.py      # 配置（.env 可覆盖）
  main.py             # FastAPI 入口，含 /health
tests/
  test_health.py
scripts/
  start.sh            # 生产启动脚本 (Uvicorn)
.gitlab-ci.yml        # GitLab CI：lint + test (+ 可选 docker-build)
Dockerfile
Makefile
requirements.txt
requirements-dev.txt
ruff.toml
pytest.ini
mypy.ini
.env.example
.gitignore
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

## 部署建议
- 生产环境建议使用 Docker 运行：
  ```bash
  docker run -p 8000:8000 --env-file .env videolingo-backend:dev
  ```
- 或在云端/容器平台使用 `Dockerfile` 构建镜像部署。
