from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

def store_chunks_in_chroma(
    embedded_chunks: List[Dict[str, Any]],
    chroma_service_url: str,
    collection_name: str = "rag_documents"
):
    """
    Stores embedded chunks in a ChromaDB collection.
    """
    print(f"Connecting to ChromaDB at {chroma_service_url} and storing chunks...")

    try:
        # Connect to ChromaDB (persistent client)
        client = chromadb.HttpClient(host=chroma_service_url.replace("http://", "").split(":")[0], port=8000)

        # Get or create the collection
        collection = client.get_or_create_collection(name=collection_name)

        # Prepare data for ChromaDB
        ids = [f"doc_{i}" for i in range(len(embedded_chunks))] # Unique IDs for each chunk
        documents = [item["text"] for item in embedded_chunks]
        metadatas = [item["metadata"] for item in embedded_chunks]
        embeddings = [item["embedding"] for item in embedded_chunks]

        # Add to ChromaDB
        collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
        print(f"Successfully added {len(embedded_chunks)} chunks to ChromaDB collection '{collection_name}'.")

    except Exception as e:
        print(f"Error storing chunks in ChromaDB: {e}")

        
# if __name__ == "__main__":
#     print("This module is meant to be imported and used by main.py or other pipeline scripts.")
#     print("Please run main.py or add dummy data for direct testing.")
    # Example dummy usage:
    # dummy_embedded_chunks = [
    #     {"text": "Text content 1", "metadata": {"page": 1}, "embedding": [0.1, 0.2, ...]},
    #     {"text": "Text content 2", "metadata": {"page": 1}, "embedding": [0.3, 0.4, ...]},
    # ]
    # CHROMADB_URL = os.getenv("CHROMADB_SERVICE_URL", "http://chromadb_service:8000")
    # store_chunks_in_chroma(dummy_embedded_chunks, CHROMADB_URL, "test_collection")