import os
import chromadb


CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
COLLECTION_NAME = "miriad_knowledge"

try:
    chroma_client = chromadb.HttpClient(
        host=CHROMA_HOST, 
        port=CHROMA_PORT
    )
    print(f"Connected to ChromaDB at http://{CHROMA_HOST}:{CHROMA_PORT}")
    
    # Delete the collection
    chroma_client.delete_collection(name=COLLECTION_NAME)
    
    print(f"\nSuccessfully deleted collection '{COLLECTION_NAME}'.")

except chromadb.errors.NotFoundError:
    print(f"Error: Collection '{COLLECTION_NAME}' not found. No action needed.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")