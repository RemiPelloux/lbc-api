# glibc-based image: curl_cffi ships wheels for linux/amd64 and linux/arm64; avoid Alpine (musl).
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app

RUN pip install --upgrade pip \
    && pip install .

EXPOSE 8000

# Settings: LBC_API_HOST, LBC_API_PORT, LBC_API_PROXY_URL, LBC_API_CLIENT_POOL_SIZE (see README)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
