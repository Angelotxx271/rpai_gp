"""Schema set-up at start-up: Alembic migrations on Postgres, create_all on SQLite (tests and local runs)."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine

from .db import is_sqlite

LOCK_ID = 727274  # one advisory lock, so two services migrating at once never collide


def config(script_location: Path, schema: str, metadata: MetaData) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(script_location))
    cfg.attributes["schema"] = schema
    cfg.attributes["metadata"] = metadata
    return cfg


def prepare(engine: Engine, metadata: MetaData, script_location: Path, schema: str) -> None:
    if is_sqlite(engine):
        metadata.create_all(engine)
        return
    cfg = config(script_location, schema, metadata)
    with engine.begin() as conn:
        cfg.attributes["connection"] = conn
        command.upgrade(cfg, "head")


def run_env() -> None:
    """Body of every migrations/env.py: migrate one schema on the connection prepare() hands over."""
    from alembic import context

    cfg = context.config
    schema, metadata = cfg.attributes["schema"], cfg.attributes["metadata"]
    conn = cfg.attributes["connection"]
    conn.exec_driver_sql(f"SELECT pg_advisory_xact_lock({LOCK_ID})")
    conn.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
    context.configure(
        connection=conn,
        target_metadata=metadata,
        version_table="alembic_version",
        version_table_schema=schema,
        include_schemas=True,
        include_name=lambda name, type_, parent: type_ != "schema" or name == schema,
    )
    with context.begin_transaction():
        context.run_migrations()
