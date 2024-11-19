# 🌘 A Lightweight FastAPI Project that enables you to host your own Jeopardy game. 🌒
## 🚀 Features:
* Ability to enable negative marks.
* Supports audio as well as image questions. 
* Supports mounting local media files and config.

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
docker run --rm -v <absolute-path-to-config-file>:/config.yaml -e CONFIG_PATH=/config.yaml -v <absolute-path-to-media-folder>:/media -p 8000:8000 sabya93/jeopardy
```