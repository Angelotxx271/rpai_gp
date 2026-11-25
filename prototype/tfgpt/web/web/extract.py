"""Text out of an uploaded proposal (.docx, .pdf, .md, .txt). Nothing is stored here."""
import io
import re

MAX_BYTES = 5 * 1024 * 1024
TYPES = (".docx", ".pdf", ".md", ".txt")


class ExtractError(Exception):
    def __init__(self, status: int, error: str, message: str):
        super().__init__(message)
        self.status, self.error, self.message = status, error, message


def docx_text(data: bytes) -> str:
    import docx

    d = docx.Document(io.BytesIO(data))
    parts = [p.text for p in d.paragraphs]
    for table in d.tables:
        for row in table.rows:
            parts.append(" | ".join(c.text.strip() for c in row.cells))
    return "\n".join(parts)


def pdf_text(data: bytes) -> str:
    import pymupdf

    with pymupdf.open(stream=data, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


def plain_text(data: bytes) -> str:
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def tidy(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def extract(filename: str, data: bytes) -> str:
    name = (filename or "").lower()
    if len(data) > MAX_BYTES:
        raise ExtractError(413, "too_long", "That file is over 5 MB.")
    try:
        if name.endswith(".docx"):
            text = docx_text(data)
        elif name.endswith(".pdf"):
            text = pdf_text(data)
        elif name.endswith((".md", ".txt")):
            text = plain_text(data)
        else:
            raise ExtractError(415, "unsupported_file", "Upload a .docx, .pdf, .md or .txt file.")
    except ExtractError:
        raise
    except Exception as ex:
        raise ExtractError(415, "unsupported_file", "That file couldn't be read. Try another format, or paste the text.") from ex
    text = tidy(text)
    if not text:
        raise ExtractError(415, "unsupported_file", "No text was found in that file (a scanned PDF has none). Paste the text instead.")
    return text
