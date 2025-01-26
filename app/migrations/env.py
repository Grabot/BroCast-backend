import asyncio
import os
from json import loads
from logging.config import fileConfig

from alembic import context
from celery.backends.database.session import ResultModelBase
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

from app.config.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = [SQLModel.metadata, ResultModelBase.metadata]

for meta in target_metadata:
    meta.naming_convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)" "s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

# add your model's MetaData object here
# for 'autogenerate' support
from app import models

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

exclude_tables = loads(os.getenv("DB_EXCLUDE_TABLES"))


def filter_db_objects(
    object,  # noqa: indirect usage
    name,
    type_,
    *args,  # noqa: indirect usage
    **kwargs  # noqa: indirect usage
):
    if type_ == "table":
        return name not in exclude_tables

    if type_ == "index" and name.startswith("idx") and name.endswith("geom"):
        return False

    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=settings.ASYNC_DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=filter_db_objects,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=filter_db_objects,
        )
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    config_section = config.get_section(config.config_ini_section)
    config_section["sqlalchemy.url"] = settings.ASYNC_DB_URL

    connectable = AsyncEngine(
        engine_from_config(
            config_section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
