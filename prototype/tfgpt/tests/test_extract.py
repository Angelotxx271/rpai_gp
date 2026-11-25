"""Check once, V5: the text extracted from a .docx, .pdf or .md is the text that gets checked."""
import io

import pytest

from tfgpt_shared import textmatch
from web.extract import ExtractError, extract

TEXT = ("Description of the intended work\n"
        "This project forecasts weekly demand for a fictional café chain using public weather data.\n"
        "Research question: how much does rain change weekday demand?")


def make_docx(text: str) -> bytes:
    import docx

    d = docx.Document()
    for line in text.split("\n"):
        d.add_paragraph(line)
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def make_pdf(text: str) -> bytes:
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_textbox(pymupdf.Rect(50, 50, 550, 800), text, fontsize=10)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.mark.parametrize("name,data", [
    ("proposal.docx", make_docx(TEXT)),
    ("proposal.pdf", make_pdf(TEXT)),
    ("proposal.md", TEXT.encode("utf-8")),
    ("proposal.txt", TEXT.encode("cp1252")),
])
def test_v5_extracted_text_equals_the_source(name, data):
    assert textmatch.normalise(extract(name, data)) == textmatch.normalise(TEXT)


def test_other_types_and_big_files_are_refused():
    with pytest.raises(ExtractError) as e:
        extract("proposal.exe", b"MZ")
    assert e.value.error == "unsupported_file"
    with pytest.raises(ExtractError) as e:
        extract("proposal.md", b"x" * (5 * 1024 * 1024 + 1))
    assert e.value.error == "too_long"


def test_a_broken_file_is_a_clear_error_not_a_crash():
    with pytest.raises(ExtractError) as e:
        extract("proposal.docx", b"not really a docx")
    assert e.value.error == "unsupported_file"


def test_the_upload_endpoint_returns_text_and_words_and_stores_nothing(stack):
    stack.start()
    r = stack.post("/api/extract", files={"file": ("p.docx", make_docx(TEXT))})
    assert r.status_code == 200 and r.json()["words"] == textmatch.words(TEXT)
    assert stack.web.get("/api/thread").json()["messages"] == []
