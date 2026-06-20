# Docker

Build from a slim Python 3.12 image, install `uv`, copy lock metadata before source for cache reuse, run `uv sync --frozen --no-dev`, use a non-root user where possible, and pass secrets at runtime. Build with `docker build -t agent-app .`; run with `docker run --env-file .env -p 7860:7860 agent-app`. Never bake `.env` into an image.
