FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1         PYTHONUNBUFFERED=1         PIP_NO_CACHE_DIR=1         PORT=8000

WORKDIR /app

# 先装依赖
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

# 拷贝代码
COPY app ./app
COPY scripts ./scripts

EXPOSE 8000
ENTRYPOINT ["bash", "scripts/start.sh"]
