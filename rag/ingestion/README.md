# SANAD/rag/ingestion/

This directory contains modules responsible for ingesting data from various sources into the SANAD RAG pipeline. This includes processing different file formats and preparing data for further steps like chunking and embedding.

## Purpose:
To efficiently and reliably collect raw data from diverse sources (e.g., PDFs, websites, databases, APIs) and transform it into a standardized format suitable for the RAG pipeline. This ensures that the knowledge base is comprehensive and up-to-date.

## Contents:
- `pdf_loader.py`: Functions for extracting text from PDF documents.
- `web_scraper.py`: Modules for scraping content from trusted websites.
- `database_extractor.py`: Functions for extracting data from structured databases.
- `api_connector.py`: Modules for connecting to and retrieving data from external APIs.

## Limitations:
- Requires robust error handling for various data sources and formats.
- Scalability considerations for handling large volumes of data.

## Needs:
- Support for multiple data formats and sources.
- Data cleaning and preprocessing capabilities.
- Mechanisms for incremental data updates.

## Usage for AI Agents:
AI agents working on the RAG pipeline should develop and maintain the ingestion modules. They must ensure that data is accurately extracted, preprocessed, and ready for subsequent steps in the RAG pipeline, adhering to the specifications in `SYSTEM_ARCHITECTURE.md`.
