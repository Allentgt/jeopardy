FROM ghcr.io/astral-sh/uv:0.5.0-python3.13-alpine
LABEL authors="sabdas"

ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

# Run the application
CMD [".venv/bin/fastapi", "run", "main.py", "--port", "8000", "--host", "0.0.0.0"]
