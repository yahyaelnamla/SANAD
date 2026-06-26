# SANAD/rag/retrievers/

This directory contains implementations of different retrieval strategies used within the SANAD RAG pipeline. These strategies are responsible for fetching relevant documents or chunks from the knowledge base based on a given query.

## Purpose:
To efficiently identify and retrieve the most relevant pieces of information from the vector store and other knowledge sources. The choice of retrieval strategy significantly impacts the quality and relevance of the information provided to the reasoning agents.

## Contents:
- `vector_retriever.py`: Implements vector-based similarity search using `pgvector`.
- `keyword_retriever.py`: Implements keyword-based search (e.g., BM25).
- `hybrid_retriever.py`: Combines vector and keyword search for improved recall and precision.
- `metadata_filter.py`: Functions for filtering retrieved documents based on metadata.

## Limitations:
- Retrieval performance can be affected by the quality of embeddings and the size of the knowledge base.
- Complex queries may require sophisticated retrieval strategies.

## Needs:
- Efficient and scalable retrieval algorithms.
- Ability to handle various query types.
- Integration with the vector store and other data sources.

## Usage for AI Agents:
AI agents working on the RAG pipeline should develop and optimize retrieval strategies within this directory. They must ensure that the retrievers can effectively fetch relevant information, contributing to the accuracy and comprehensiveness of the SANAD platform's responses.
