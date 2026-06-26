# SANAD/rag/chunking/

This directory contains modules responsible for breaking down large documents into smaller, manageable chunks suitable for embedding and retrieval within the SANAD RAG pipeline.

## Purpose:
To optimize the retrieval process by ensuring that individual pieces of information are of an appropriate size for vector embedding and semantic search. Effective chunking helps in retrieving precise and relevant information without overwhelming the language model.

## Contents:
- `text_splitter.py`: Functions for splitting text based on various strategies (e.g., character, token, sentence, recursive).
- `markdown_splitter.py`: Specialized splitter for Markdown documents.
- `html_splitter.py`: Specialized splitter for HTML content.

## Limitations:
- The optimal chunk size can vary depending on the content and the embedding model used.
- Overlapping chunks might be necessary to preserve context.

## Needs:
- Flexible chunking strategies.
- Ability to handle different document formats.
- Preservation of contextual information across chunks.

## Usage for AI Agents:
AI agents working on the RAG pipeline should implement and refine chunking strategies within this directory. They must ensure that the chunking process effectively prepares documents for embedding and retrieval, contributing to the overall accuracy of the RAG system.
