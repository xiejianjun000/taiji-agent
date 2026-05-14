FROM python:3.11-slim

LABEL maintainer="OpenTaiji Team <contact@opentaiji.com>"
LABEL description="govmcp - 国产信创MCP协议"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir ".[full,ws,http]"

COPY govmcp/ ./govmcp/
COPY tests/ ./tests/
COPY docs/ ./docs/
COPY scripts/ ./scripts/

RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000

CMD ["python", "-m", "govmcp"]
