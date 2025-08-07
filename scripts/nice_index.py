import os
import requests
import chromadb
import json
from chromadb.utils import embedding_functions

# --- Configuration ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
TEI_HOST = os.getenv("TEI_HOST", "tei_service")
TEI_PORT = os.getenv("TEI_PORT", "80")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# NICE API config (placeholder)
NICE_API_KEY = os.getenv("NICE_API_KEY", "your_api_key_here")  # Set this when you get it
NICE_API_BASE_URL = "https://api.nice.org.uk"  # Replace with real NICE API base

SAFE_PAYLOAD_LIMIT_BYTES = 500000
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
        response = requests.post(tei_url, json={"inputs": texts})
        response.raise_for_status()
        return response.json()

except requests.exceptions.RequestException as e:
    print(f"Error connecting to a service: {e}")
    exit(1)

# --- Simulated NICE API Call ---
def fetch_nice_guidance():
    print("Simulating NICE API call...")
    # Simulated structure – match actual NICE API response when known
    return [
        {"id": "nice_001", "title": "Diabetes in adults", "summary": "Management of type 2 diabetes in adults."},
        {"id": "nice_002", "title": "Asthma: diagnosis and monitoring", "summary": "Recommendations for diagnosing asthma."},
        {"id": "nice_003", "title": "Depression in children and young people", "summary": "Treatment and care for depression in youth."}
    ]

# --- Main Indexing Logic ---
def index_nice_knowledge():
    collection_name = "nice_knowledge"

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

    data = fetch_nice_guidance()

    current_batch_docs = []
    current_batch_ids = []
    current_payload_size = 0
    document_counter = 0
    total_docs = len(data)

    for entry in data:
        document = f"Title: {entry['title']}\nSummary: {entry['summary']}"
        doc_id = entry["id"]
        doc_size = len(json.dumps(document))

        if (current_payload_size + doc_size > SAFE_PAYLOAD_LIMIT_BYTES) or (len(current_batch_docs) >= MAX_DOCS_PER_BATCH):
            if current_batch_docs:
                try:
                    embeddings = tei_embedding_function(current_batch_docs)
                    collection.add(
                        documents=current_batch_docs,
                        embeddings=embeddings,
                        ids=current_batch_ids
                    )
                    print(f"Ingested {document_counter} / {total_docs} documents.")
                except requests.exceptions.HTTPError as e:
                    print(f"Error getting embeddings from TEI: {e}")
                    raise e

            # Reset
            current_batch_docs = [document]
            current_batch_ids = [doc_id]
            current_payload_size = doc_size
        else:
            current_batch_docs.append(document)
            current_batch_ids.append(doc_id)
            current_payload_size += doc_size

        document_counter += 1

    # Final batch
    if current_batch_docs:
        try:
            embeddings = tei_embedding_function(current_batch_docs)
            collection.add(
                documents=current_batch_docs,
                embeddings=embeddings,
                ids=current_batch_ids
            )
            print(f"Ingested {document_counter} / {total_docs} documents.")
        except requests.exceptions.HTTPError as e:
            print(f"Error (final batch): {e}")
            raise e

    print(f"\nIndexing complete! The '{collection_name}' collection is ready to use.")

if __name__ == "__main__":
    index_nice_knowledge()
