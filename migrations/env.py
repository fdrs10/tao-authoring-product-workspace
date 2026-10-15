import logging
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    logging.getLogger(__name__)

# Cloud-compatible: the DB connection always comes from the environment
# (Cloud SQL socket/unix socket or DATABASE_URL), never hard-coded.
target_url = os.environ.get("DATABASE_URL") or os.environ.get("DB_URL")
if not target_url:
    raise RuntimeError(
        "DATABASE_URL is required for Alembic migrations "
        "(e.g. postgresql+psycopg://user:pass@host:5432/dbname)."
    )
config.set_main_option("sqlalchemy.url", target_url)


def run_migrations_offline() -> None:
    context.configure(
        url=target_url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
