"""The document pack: the programme's documents, loaded by us, numbered by section so every citation can be checked."""
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from tfgpt_shared import textmatch

from .models import DocPack, Document, Programme

HEADING = re.compile(r"^(#{1,6})[ \t]+(\S[^\r\n]*)$")
PROGRAMME = ("bdba", "Data and Business Analytics")


@dataclass
class Section:
    sid: str
    level: int
    title: str
    path: str
    body: str
    full: str = ""  # its own text plus every subsection's, for checking answer quotes


@dataclass
class Pack:
    id: int
    title: str
    sha12: str
    sections: list[Section]
    by_id: dict[str, Section] = field(default_factory=dict)
    text: str = ""

    def __post_init__(self):
        self.by_id = {s.sid: s for s in self.sections}
        self.text = render(self.sections)


def parse(markdown: str) -> list[Section]:
    """Split Markdown at its headings; each heading becomes S1, S2, ... in order. Text before the first heading is S0."""
    sections, stack, lines = [], [], []
    cur = Section("S0", 0, "Preamble", "Preamble", "")

    def close():
        cur.body = "\n".join(lines).strip()
        if cur.sid != "S0" or cur.body:
            sections.append(cur)

    n = 0
    for line in markdown.splitlines():
        m = HEADING.match(line)
        if not m:
            lines.append(line)
            continue
        close()
        lines = []
        n += 1
        level, title = len(m.group(1)), m.group(2).strip()
        stack = [s for s in stack if s.level < level]
        path = " > ".join([s.title for s in stack] + [title])
        cur = Section(f"S{n}", level, title, path, "")
        stack.append(cur)
    close()
    for i, s in enumerate(sections):
        parts = [s.body]
        for t in sections[i + 1:]:
            if t.level <= s.level:
                break
            parts.append(t.title + "\n" + t.body)
        s.full = "\n".join(parts)
    return sections


def render(sections: list[Section]) -> str:
    """The pack as the model sees it: every heading carries its id, e.g. "## [S12] Preliminary timeline"."""
    out = []
    for s in sections:
        if s.level:
            out.append(f"{'#' * s.level} [{s.sid}] {s.title}")
        if s.body:
            out.append(s.body)
        out.append("")
    return "\n".join(out).strip()


def load(db: Session, markdown: str, title: str, stage: str = "proposal") -> DocPack:
    """Store a pack and make it the active one for its stage. The text never goes in the repository."""
    if not db.get(Programme, PROGRAMME[0]):
        db.add(Programme(code=PROGRAMME[0], name=PROGRAMME[1]))
        db.flush()
    sections = parse(markdown)
    sha = hashlib.sha256(markdown.encode("utf-8")).hexdigest()[:12]
    db.execute(update(DocPack).where(DocPack.programme == PROGRAMME[0], DocPack.stage == stage).values(active=False))
    pack = DocPack(programme=PROGRAMME[0], stage=stage, title=title, sha12=sha, active=True, sections=len(sections))
    db.add(pack)
    db.flush()
    for i, s in enumerate(sections):
        db.add(Document(pack_id=pack.id, position=i, sid=s.sid, level=s.level, title=s.title, path=s.path, body=s.body))
    db.flush()
    _cache.clear()
    return pack


_cache: dict[int, Pack] = {}


def active(db: Session, stage: str = "proposal") -> Pack | None:
    row = db.scalars(select(DocPack).where(DocPack.programme == PROGRAMME[0], DocPack.stage == stage,
                                           DocPack.active.is_(True)).order_by(DocPack.id.desc())).first()
    if not row:
        return None
    if row.id not in _cache:
        docs = db.scalars(select(Document).where(Document.pack_id == row.id).order_by(Document.position))
        sections = [Section(d.sid, d.level, d.title, d.path, d.body) for d in docs]
        for i, s in enumerate(sections):  # rebuild the subsection text used for quote checks
            parts = [s.body]
            for t in sections[i + 1:]:
                if t.level <= s.level:
                    break
                parts.append(t.title + "\n" + t.body)
            s.full = "\n".join(parts)
        _cache[row.id] = Pack(row.id, row.title, row.sha12, sections)
    return _cache[row.id]


def quote_in_section(pack: Pack, sid: str, quote: str) -> bool:
    s = pack.by_id.get(sid)
    return bool(s) and textmatch.find(quote, s.title + "\n" + s.full)


def from_file(db: Session, path: Path, title: str | None = None) -> DocPack:
    return load(db, path.read_text(encoding="utf-8"), title or path.stem)
