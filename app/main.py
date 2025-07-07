import os
import sys
import pysqlite3
from dotenv import load_dotenv

# Monkey-patch sqlite3 before anything else that might import it
sys.modules["sqlite3"] = pysqlite3
sys.modules["_sqlite3"] = pysqlite3.dbapi2

load_dotenv()

from app.data_ingestion.document_loader import load_documents
from app.data_ingestion.split_and_chunk import split_documents_into_chunks
from app.embed_and_store.embed import create_embeddings
from app.embed_and_store.store import store_chunks_in_chroma

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

    # 2. Split and Chunk Documents
    print("Step 2: Splitting documents into chunks...")
    chunks = split_documents_into_chunks(documents)
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

    # 1. Create Embeddings
    print("Step 1: Generating embeddings for chunks...")
    # This function will call your tei_service
    embedded_chunks = create_embeddings(chunks, os.getenv("TEI_SERVICE_URL"))
    if not embedded_chunks:
        print("No embeddings generated. Exiting embedding pipeline.")
        return

    # 2. Store Embeddings in Vector DB
    print("Step 2: Storing embeddings and chunks in ChromaDB...")
    # This function will call your chromadb_service
    store_chunks_in_chroma(embedded_chunks, os.getenv("CHROMADB_SERVICE_URL"), os.getenv("CHROMA_COLLECTION_NAME"))
    print("Embedding and Storage pipeline complete.")


def main():
    """
    Main function to orchestrate the RAG application.
    """
    load_dotenv()

    RAW_DATA_DIRECTORY = os.getenv("RAW_DATA_DIRECTORY", "/rag_app/data/raw_data")
    
    # --- Ingestion Pipeline ---
    processed_chunks = run_ingestion_pipeline(RAW_DATA_DIRECTORY)
    
    if processed_chunks:
        # --- Embedding and Storage Pipeline ---
        run_embedding_and_storage_pipeline(processed_chunks)

        print("\n--- All data indexed. Ready for Retrieval and Generation ---")

        # --- Retrieval and Generation Pipeline (next major phase) ---
        # query = "What is the main diagnosis in the soap note?"
        # relevant_chunks = retrieve_relevant_chunks(query, os.getenv("CHROMA_DB_HOST"))
        # summary = generate_summary(relevant_chunks, query, os.getenv("TGI_SERVICE_URL"))
        print("Querying and Summary generation step would go here.")
    else:
        print("No chunks to process. RAG pipeline halted.")

if __name__ == "__main__":
    main()