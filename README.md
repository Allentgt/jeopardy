## Fun Little Project to get you started on making your own Jeopardy game using FastAPI.

### Build with Docker

```bash
docker build -t jeopardy .
```

### Run with Docker

```bash
docker run -p 8000:8000 --rm jeopardy
```

### Or just run by pulling from Docker Hub

```bash
docker run -p 8000:8000 --rm sabya93/jeopardy
```

### To run with a different config file from the host machine

```bash
docker run --rm -v <absolute-path-to-config-file>:/app/config.yaml -e CONFIG_PATH=/app/config.yaml -p 8000:8000 sabya93/jeopardy
```