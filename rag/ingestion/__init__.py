"""Data ingestion modules for the SANAD RAG pipeline."""

from rag.ingestion.base import IngestedDocument
from rag.ingestion.pdf_loader import load_pdf

__all__ = ["IngestedDocument", "load_pdf"]
