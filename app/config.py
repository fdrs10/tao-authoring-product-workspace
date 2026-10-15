"""Runtime configuration — all from the environment (Cloud Run contract §15)."""

import os


class Settings:
    app_env: str = os.environ.get("APP_ENV", "local")
    port: int = int(os.environ.get("PORT", "8080"))
    database_url: str | None = os.environ.get("DATABASE_URL") or os.environ.get(
        "DB_URL"
    )
    log_json: bool = os.environ.get("LOG_FORMAT", "json") == "json"
    version: str = "2.0.0"


settings = Settings()
