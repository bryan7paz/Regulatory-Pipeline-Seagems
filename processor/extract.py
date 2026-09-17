"""Text extraction from documents (PDF via PyMuPDF, HTML via BeautifulSoup)."""
from __future__ import annotations

from pathlib import Path


def extract_text(content: bytes, content_type: str) -> str:
    """Extract plain text from raw document bytes."""
    if content_type == "pdf":
        return _extract_pdf(content)
    return _extract_html(content)


def extract_from_file(path: str, content_type: str) -> str:
    return extract_text(Path(path).read_bytes(), content_type)


def _extract_pdf(content: bytes) -> str:
    import fitz  # PyMuPDF

    with fitz.open(stream=content, filetype="pdf") as doc:
        pages = [page.get_text("text") for page in doc]
    return "\n".join(pages)


def _extract_html(content: bytes) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text("\n", strip=True)