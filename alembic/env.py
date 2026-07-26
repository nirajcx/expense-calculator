"""
alembic/env.py — Alembic Environment Configuration
=====================================================

This file tells Alembic:
  1. WHERE the database is (connection URL from our settings)
  2. WHAT models to track (by importing our Base and all models)
  3. HOW to run migrations (online mode for connected DB)

You usually don't need to modify this file. Alembic generates it,
and we've customized it to read our app's config.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ──────────────────────────────────────────────
# IMPORTANT: Import Base and ALL models here
# ──────────────────────────────────────────────
# Alembic needs to "see" all models to detect changes.
# If you add a new model file, import it here too!
from app.db.base import Base
from app.models.user import User          # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.expense import Expense    # noqa: F401
from app.core.config import settings

# Alembic Config object — gives access to alembic.ini values
config = context.config

# Set the database URL from our app settings (overrides alembic.ini)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Tell Alembic which metadata to use for autogenerate
# (Base.metadata contains info about all our tables)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — generates SQL without connecting to DB.
    Useful for generating migration scripts to review before applying.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode — connects to the database and applies changes.
    This is the normal way migrations run.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine which mode to run in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
