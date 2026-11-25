"""Load the programme's documents into the database: python -m advisor.loadpack <file.md> [--title ...] [--until HEADING]

Run it from your own machine against the database (DATABASE_URL); the documents never enter the repository.
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
    args = ap.parse_args(argv)
    text = args.file.read_text(encoding="utf-8")
    if args.until:
        lines = text.splitlines()
        cut = next((i for i, line in enumerate(lines) if line.startswith(args.until)), len(lines))
        text = "\n".join(lines[:cut]).rstrip() + "\n"
    database = Database(make_engine())
    prepare(database.engine, Base.metadata, MIGRATIONS, SCHEMA)
    with database.session() as db:
        p = pack.load(db, text, args.title or args.file.stem)
        print(f"loaded pack {p.id} ({p.sha12}): {p.sections} sections, {len(text):,} characters, now active")


if __name__ == "__main__":
    main()
