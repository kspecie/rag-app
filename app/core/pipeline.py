import os
import sys
import pysqlite3 
from typing import Optional

# workaround for chromadb/sqlite3 before anything else that might import it
sys.modules["sqlite3"] = pysqlite3
sys.modules["_sqlite3"] = pysqlite3.dbapi2


from app.data_ingestion.document_loader import load_documents
from app.data_ingestion.split_and_chunk import clean_document_content
from app.data_ingestion.split_and_chunk import split_documents_into_chunks
from app.embed_and_store.embed import create_embeddings
from app.embed_and_store.store import store_chunks_in_chroma
from app.retrieval.retrieve import retrieve_relevant_chunks
from app.generation.generate_summary import generate_summary


def run_ingestion_pipeline(raw_data_dir: str):
    """
    Runs the document ingestion pipeline: loads, splits, and chunks documents.
    """
    print("\n--- Starting Document Ingestion Pipeline ---")

    # 1. Load Documents
    print("Step 1: Loading documents...")
    documents = load_documents(raw_data_dir)
    if not documents:
        print("No documents loaded. Exiting ingestion pipeline.")
        return [] # Return an empty list if no docs

    # 2. Clean, Split and Chunk Documents
    print("Step 2: Cleaning then Splitting documents into chunks...")
    clean_documents = clean_document_content(documents)
    print("Documents have been cleaned.")
    chunks = split_documents_into_chunks(clean_documents)
    if not chunks:
        print("No chunks generated. Exiting ingestion pipeline.")
        return []

    print(f"Ingestion pipeline complete. Generated {len(chunks)} chunks.")
    return chunks

def run_embedding_and_storage_pipeline(chunks: list):
    """
    Generates embeddings for chunks and stores them in the vector database.
    """
    print("\n--- Starting Embedding and Storage Pipeline ---")

    # 3. Create Embeddings
    print("Step 3: Generating embeddings for chunkss...")
    embedded_chunks = create_embeddings(chunks, os.getenv("TEI_SERVICE_URL"))
    if not embedded_chunks:
        print("No embeddings generated. Exiting embedding pipeline.")
        return

    # 4. Store Embeddings in Vector DB
    print("Step 4: Storing embeddings and chunks in ChromaDB...")
    store_chunks_in_chroma(embedded_chunks, os.getenv("CHROMADB_SERVICE_URL"), os.getenv("CHROMA_COLLECTION_NAME"))
    print("Embedding and Storage pipeline complete.")


def run_retrieval_and_generation_pipeline(transcribed_conversation: str, additional_content: Optional[str] = None):
    """
    Runs the retrieval and generation pipeline: retrieves relevant chunks and generates a summary.
    """
    print("\n--- Starting Retrieval and Generation Pipeline ---")

    # 5. Retrieve Relevant Chunks
    print(f"Step 5: Retrieving relevant chunks for query")
    relevant_chunks = retrieve_relevant_chunks(transcribed_conversation, os.getenv("CHROMADB_SERVICE_URL"), n_results=7)
    if not relevant_chunks:
        print("No relevant chunks found. Cannot generate summary.")
        return None

    print(f"Found {len(relevant_chunks)} relevant chunks. These are the relevant chunks: '{relevant_chunks}'")

    # 6. Generate Summary
    print("Step 6: Generating summary...")
    print(f"Inside pipeline, received additional_content: {additional_content}")
    summary = generate_summary(transcribed_conversation, relevant_chunks, os.getenv("TGI_SERVICE_URL"), additional_content=additional_content)
    if not summary:
        print("Failed to generate summary.")
        return None

    print("\n--- Generated Summary ---")
    print(summary)
    print("--- End Summary ---")
    print("Retrieval and Generation pipeline complete.")
    return summary



