# Placeholder target container. Replace with implementation-specific multi-stage build.
FROM python:3.12-slim
WORKDIR /app
COPY . /app
CMD ["python", "-m", "http.server", "8080"]
