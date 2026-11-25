"""Settings read from environment variables, so configuration stays out of the code."""
import os

PROGRAMME = "Data and Business Analytics · Full Proposal"


def env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


def env_int(name: str, default: int) -> int:
    return int(env(name, str(default)))


def env_float(name: str, default: float) -> float:
    return float(env(name, str(default)))


def env_bool(name: str, default: bool) -> bool:
    return (env(name, "1" if default else "0") or "").lower() in {"1", "true", "yes", "on"}


def env_list(name: str) -> list[str]:
    return [x.strip() for x in (env(name, "") or "").split(",") if x.strip()]


def version() -> str:
    """The commit the service runs, so /healthz shows which code is live."""
    sha = env("APP_VERSION") or env("RAILWAY_GIT_COMMIT_SHA") or "dev"
    return sha[:7] if len(sha) >= 40 else sha
