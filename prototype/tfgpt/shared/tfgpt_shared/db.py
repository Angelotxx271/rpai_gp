"""One Postgres instance, one schema per service. Tests may run on SQLite, where the schemas are mapped away."""
from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy import JSON, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .settings import env

SCHEMAS = ("app", "advisor", "harness", "eval")
# JSONB on Postgres, plain JSON elsewhere
JSONType = JSON().with_variant(JSONB(), "postgresql")


def now() -> datetime:
    return datetime.now(timezone.utc)


def aware(dt: datetime | None) -> datetime | None:
    """SQLite drops the time zone; every stored time is UTC."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def normalise_url(url: str) -> str:
    """Railway gives postgres:// or postgresql://; SQLAlchemy needs the psycopg 3 driver named."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def database_url() -> str:
    return normalise_url(env("DATABASE_URL", "sqlite:///./tfgpt-dev.sqlite"))


def make_engine(url: str | None = None) -> Engine:
    url = normalise_url(url or database_url())
    if url.startswith("sqlite"):
        kwargs = {"connect_args": {"check_same_thread": False}}
        if url in ("sqlite://", "sqlite:///:memory:"):
            kwargs["poolclass"] = StaticPool
        engine = create_engine(url, **kwargs)
        return engine.execution_options(schema_translate_map={s: None for s in SCHEMAS})
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10)


def is_sqlite(engine: Engine) -> bool:
    return engine.dialect.name == "sqlite"


class Database:
    """A session factory bound to one engine; each service holds one."""

    def __init__(self, engine: Engine):
        self.engine = engine
        self.factory = sessionmaker(bind=engine, expire_on_commit=False)

    @contextmanager
    def session(self):
        s: Session = self.factory()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()
