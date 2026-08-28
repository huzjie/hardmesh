# hardmesh 控制面镜像
FROM python:3.12-slim AS base

WORKDIR /app

# 内核零依赖，仅需 FastAPI + uvicorn 提供控制面
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hardmesh/ hardmesh/
COPY config.example.json config.example.json
COPY LICENSE .
COPY README.md .

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz', timeout=3)" || exit 1

ENTRYPOINT ["python", "-m", "hardmesh", "serve", "--host", "0.0.0.0", "--port", "8080"]
