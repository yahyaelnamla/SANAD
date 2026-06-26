# SANAD/rag/pipelines/

This directory contains modules responsible for orchestrating the end-to-end workflow of the Retrieval-Augmented Generation (RAG) pipeline. It defines how different RAG components (ingestion, chunking, embeddings, retrieval, re-ranking) are integrated and executed.

## Purpose:
To define and manage the complete flow of data through the RAG system, from raw data ingestion to the final retrieval of relevant information. This ensures a coherent and efficient process for grounding the AI agents' responses.

## Contents:
- `main_rag_pipeline.py`: The primary orchestration logic for the RAG pipeline.
- `ingestion_pipeline.py`: Defines the workflow for data ingestion and preprocessing.
- `retrieval_pipeline.py`: Defines the workflow for query processing and document retrieval.

## Limitations:
- Complexity can increase with more sophisticated RAG strategies.
- Requires careful management of dependencies between different RAG components.

## Needs:
- Clear definition of the sequence of operations.
- Robust error handling and logging throughout the pipeline.
- Flexibility to adapt to different RAG configurations.

## Usage for AI Agents:
AI agents working on the RAG pipeline should implement the orchestration logic within this directory. They must ensure that all RAG components are correctly integrated and that the pipeline functions efficiently and reliably to provide accurate information to the reasoning agents.
