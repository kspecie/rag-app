import os
import chromadb
from chromadb import Client

def list_collections_and_documents_with_content():
    """
    Connects to a ChromaDB instance, lists all collections, and
    for each collection, prints document IDs and their content.
    """
    CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8003"))

    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collections = client.list_collections()

        if not collections:
            print("No collections found in ChromaDB.")
            return

        print(f"Connected to ChromaDB at http://{CHROMA_HOST}:{CHROMA_PORT}")
        print(f"Found {len(collections)} collections:")

        for coll in collections:
            print(f"\n--- Collection: {coll.name} ---")
            
            collection = client.get_collection(name=coll.name)
            
            # The `get()` method with no arguments returns all documents in the collection
            documents_data = collection.get() 
            
            ids = documents_data['ids']
            documents = documents_data['documents']
            
            if ids:
                print(f" - Document count: {len(ids)}")
                print(" - Documents:")
                for doc_id, doc_content in zip(ids, documents):
                    print(f"   - ID: {doc_id}")
                    print(f"     Content: {doc_content[:500]}...")
            else:
                print(" - No documents found in this collection.")

    except Exception as e:
        print(f"Failed to connect or fetch collections: {e}")

if __name__ == "__main__":
    list_collections_and_documents_with_content()
