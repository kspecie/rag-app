import os
import requests
import chromadb
import json
import tiktoken
from datasets import load_dataset
from chromadb.utils import embedding_functions
from typing import List

# --- Configuration ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
TEI_HOST = os.getenv("TEI_HOST", "tei_service")
TEI_PORT = os.getenv("TEI_PORT", "80")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
MAX_CHUNK_TOKENS = 450  # A safe token limit to avoid TGI overflow
CHUNK_OVERLAP_TOKENS = 150 # Small overlap to preserve context
MAX_DOCS_PER_BATCH = 16

# --- Initialize Clients ---
try:
    chroma_client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT
    )
    print(f"Connected to ChromaDB at http://{CHROMA_HOST}:{CHROMA_PORT}")

    def tei_embedding_function(texts):
        tei_url = f"http://{TEI_HOST}:{TEI_PORT}/embed"
        response = requests.post(
            tei_url,
            json={"inputs": texts}
        )
        response.raise_for_status()
        return response.json()

except requests.exceptions.RequestException as e:
    print(f"Error connecting to a service: {e}")
    exit(1)

# ---Token-based Chunking Function ---
def tokenize_and_chunk(text: str, max_tokens: int, overlap: int) -> List[str]:
    """Splits a string into token-limited chunks with overlap."""
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        # Ensure the chunk doesn't end mid-word if possible
        chunk_tokens = tokens[start:end]
        chunks.append(encoder.decode(chunk_tokens))
        
        start += max_tokens - overlap
        if start < 0:
            start = 0
            
    return chunks

# --- Main Indexing Logic ---
def index_miriad_dataset():
    collection_name = "miriad_knowledge"

    try:
        chroma_client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists. Skipping indexing.")
        return
    except chromadb.errors.NotFoundError:
        print(f"Collection '{collection_name}' not found. Creating and indexing...")

    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    )

    print("Loading Miriad dataset...")
    try:
        dataset = load_dataset("miriad/miriad-5.8M", split="train[:50000]")
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return

    total_docs = len(dataset)
    current_batch_docs = []
    current_batch_ids = []
    document_counter = 0

    print("Starting token-based chunking and embedding...")
    for i, row in enumerate(dataset):
        document = f"Question: {row['question']}\nAnswer: {row['answer']}"
        
        # --- chunking function ---
        chunks = tokenize_and_chunk(document, max_tokens=MAX_CHUNK_TOKENS, overlap=CHUNK_OVERLAP_TOKENS)

        for j, chunk in enumerate(chunks):
            doc_id = f"miriad_{i}_chunk_{j}"
            current_batch_docs.append(chunk)
            current_batch_ids.append(doc_id)
            document_counter += 1

            # Check if the batch is ready for embedding
            if len(current_batch_docs) >= MAX_DOCS_PER_BATCH:
                try:
                    embeddings = tei_embedding_function(current_batch_docs)
                    collection.add(
                        documents=current_batch_docs,
                        embeddings=embeddings,
                        ids=current_batch_ids
                    )
                    print(f"Ingested {document_counter} chunks from Miriad dataset.")
                except requests.exceptions.HTTPError as e:
                    print(f"Error getting embeddings from TEI: {e}")
                    raise e
                
                # Reset for next batch
                current_batch_docs = []
                current_batch_ids = []

    # Final batch
    if current_batch_docs:
        try:
            embeddings = tei_embedding_function(current_batch_docs)
            collection.add(
                documents=current_batch_docs,
                embeddings=embeddings,
                ids=current_batch_ids
            )
            print(f"Ingested final {len(current_batch_docs)} chunks from Miriad dataset.")
        except requests.exceptions.HTTPError as e:
            print(f"Error getting embeddings from TEI (final batch): {e}")
            raise e

    print(f"\nIndexing complete! Total chunks added: {document_counter}.")

if __name__ == "__main__":
    index_miriad_dataset()


