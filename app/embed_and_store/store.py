from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from  datetime import datetime

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
        # Connect to ChromaDB 
        client = chromadb.HttpClient(host=chroma_service_url.replace("http://", "").split(":")[0], port=8000)

        # Get or create the collection
        collection = client.get_or_create_collection(name=collection_name)

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for i, item in enumerate(embedded_chunks):
            source = item["metadata"].get("source", "unknown_source")
            chunk_id = f"{source}_chunk_{i}"

            # Ensure upload_date exists in metadata
            if "upload_date" not in item["metadata"]:
                item["metadata"]["upload_date"] = datetime.utcnow().isoformat()
            
            ids.append(chunk_id)
            documents.append(item["text"])
            metadatas.append(item["metadata"])
            embeddings.append(item["embedding"])

        #print("CHUNK IDS:", ids)
        print("METADATAS:", metadatas)
        
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

        
