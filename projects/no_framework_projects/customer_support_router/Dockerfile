FROM python:3.12-slim

ARG UV_VERSION=0.8.3
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app
RUN pip install --no-cache-dir "uv==${UV_VERSION}"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app.py ./
COPY src ./src
COPY prompts ./prompts
COPY data ./data

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app /opt/venv
USER appuser

EXPOSE 7860
CMD ["python", "app.py"]

