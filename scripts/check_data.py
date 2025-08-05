import os
import chromadb

def list_all_collections():
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
            print(f"Collection name: {coll.name}")
            collection = client.get_collection(name=coll.name)
            print(f" - Document count: {collection.count()}")

    except Exception as e:
        print(f"Failed to connect or fetch collections: {e}")

if __name__ == "__main__":
    list_all_collections()
