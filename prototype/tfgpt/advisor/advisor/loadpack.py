"""Load the programme's documents: python -m advisor.loadpack <file.md> [--title ...] [--until HEADING] [--url URL]

Without --url it writes to DATABASE_URL directly. With --url it uploads to the live web service's loader, with
ADMIN_TOKEN from the environment. Either way the documents never enter the repository.
"""
import argparse
from pathlib import Path

from tfgpt_shared.db import Database, make_engine
from tfgpt_shared.migrate import prepare

from . import pack
from .app import MIGRATIONS
from .models import SCHEMA, Base


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="advisor.loadpack")
    ap.add_argument("file", type=Path)
    ap.add_argument("--title", default=None)
    ap.add_argument("--until", default=None, help="stop before the first line that starts with this text")
    ap.add_argument("--url", default=None, help="the live web service, for example https://...up.railway.app")
    args = ap.parse_args(argv)
    text = args.file.read_text(encoding="utf-8")
    if args.until:
        lines = text.splitlines()
        cut = next((i for i, line in enumerate(lines) if line.startswith(args.until)), len(lines))
        text = "\n".join(lines[:cut]).rstrip() + "\n"
    if args.url:
        import os

        import httpx

        r = httpx.post(f"{args.url.rstrip('/')}/api/admin/pack", timeout=120,
                       files={"file": ("pack.md", text.encode("utf-8"), "text/markdown")},
                       headers={"X-TFGPT": "1", "X-Admin-Token": os.environ["ADMIN_TOKEN"],
                                "X-Pack-Title": args.title or args.file.stem})
        r.raise_for_status()
        p = r.json()
        print(f"loaded pack {p['id']} ({p['sha12']}): {p['sections']} sections, {len(text):,} characters, now active")
        return
    database = Database(make_engine())
    prepare(database.engine, Base.metadata, MIGRATIONS, SCHEMA)
    with database.session() as db:
        p = pack.load(db, text, args.title or args.file.stem)
        print(f"loaded pack {p.id} ({p.sha12}): {p.sections} sections, {len(text):,} characters, now active")


if __name__ == "__main__":
    main()
