FROM ghcr.io/astral-sh/uv:0.5.0-python3.13-bookworm-slim
LABEL authors="sabdas"

ADD . .

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

# Run the application
CMD [".venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]
