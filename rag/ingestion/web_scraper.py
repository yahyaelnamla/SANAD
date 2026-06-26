"""Web content ingestion from trusted URLs."""

import httpx
from bs4 import BeautifulSoup

from rag.ingestion.base import IngestedDocument


def scrape_web_page(
    url: str,
    source_title: str,
    source_author: str,
    language: str = "ar",
    timeout: float = 30.0,
) -> IngestedDocument:
    """Fetch and extract readable text from a trusted web page."""
    response = httpx.get(url, timeout=timeout, follow_redirects=True)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    if not text.strip():
        raise ValueError(f"No extractable text from URL: {url}")

    return IngestedDocument(
        content=text,
        source_title=source_title,
        source_author=source_author,
        language=language,
        metadata={"format": "web", "url": url},
    )
