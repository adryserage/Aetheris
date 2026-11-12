# Hosted Aetheris MCP server (aetheris serve --http), published behind MCP Hub.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /src
COPY pyproject.toml README.md LICENSE NOTICE ./
COPY aetheris ./aetheris
RUN pip install ".[hosted]" && rm -rf /src

RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin aetheris
USER aetheris
WORKDIR /

ENV PORT=8080
EXPOSE 8080
CMD ["aetheris", "serve", "--http"]
