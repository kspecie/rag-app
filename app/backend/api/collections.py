#app/backend/api/collections_update.py
import os
import chromadb
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from datetime import datetime
import json
from datasets import load_dataset
from chromadb.utils import embedding_functions
import requests
import re
import hashlib
import tiktoken

from scripts.index_miriad import index_miriad_dataset
from scripts.nice_index import index_nice_knowledge


CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
TEI_HOST = os.getenv("TEI_HOST", "tei_service")
TEI_PORT = os.getenv("TEI_PORT", "80")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
MAX_CHUNK_TOKENS = 450
CHUNK_OVERLAP_TOKENS = 150
MAX_DOCS_PER_BATCH = 16

router = APIRouter(
    prefix="/collections", # All endpoints in this router will start with /collections
    tags=["Collections"], # For grouping in Swagger UI
)

# Initialize Chroma client
chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

def tei_embedding_function(texts):
    tei_url = f"http://{TEI_HOST}:{TEI_PORT}/embed"
    response = requests.post(tei_url, json={"inputs": texts})
    response.raise_for_status()
    return response.json()

def tokenize_and_chunk(text: str, max_tokens: int, overlap: int):
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunks.append(encoder.decode(chunk_tokens))
        start += max_tokens - overlap
        if start < 0:
            start = 0
    return chunks
    

@router.get("/")
def get_collections_metadata() -> Dict[str, Any]:
    """
    Get metadata for all collections including last_updated timestamps.
    """
    try:
        collections = chroma_client.list_collections()
        metadata = {}
        
        for collection in collections:
            try:
                # Get collection metadata
                collection_obj = chroma_client.get_collection(name=collection.name)
                # Try to get last_updated from metadata
                last_updated = None
                if hasattr(collection_obj, 'metadata') and collection_obj.metadata:
                    last_updated = collection_obj.metadata.get('last_updated')
                
                metadata[collection.name] = {
                    'last_updated': last_updated
                }
            except Exception as e:
                print(f"Error getting metadata for collection {collection.name}: {e}")
                metadata[collection.name] = {'last_updated': None}
        
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_miriad")
def update_miriad() -> Dict[str, str]:
    collection_name = "miriad_knowledge"
    try:
        chroma_client.get_collection(name=collection_name)
        return {"message": f"Collection '{collection_name}' already exists. Skipping indexing."}
    except chromadb.errors.NotFoundError:
        collection = chroma_client.create_collection(
            name=collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        )

    try:
        dataset = load_dataset("miriad/miriad-5.8M", split="train[:20000]")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dataset: {e}")

    current_batch_docs = []
    current_batch_ids = []
    document_counter = 0

    for i, row in enumerate(dataset):
        document = f"Question: {row['question']}\nAnswer: {row['answer']}"
        chunks = tokenize_and_chunk(document, MAX_CHUNK_TOKENS, CHUNK_OVERLAP_TOKENS)
        for j, chunk in enumerate(chunks):
            doc_id = f"miriad_{i}_chunk_{j}"
            current_batch_docs.append(chunk)
            current_batch_ids.append(doc_id)
            document_counter += 1
            if len(current_batch_docs) >= MAX_DOCS_PER_BATCH:
                embeddings = tei_embedding_function(current_batch_docs)
                collection.add(documents=current_batch_docs, embeddings=embeddings, ids=current_batch_ids)
                current_batch_docs, current_batch_ids = [], []

    if current_batch_docs:
        embeddings = tei_embedding_function(current_batch_docs)
        collection.add(documents=current_batch_docs, embeddings=embeddings, ids=current_batch_ids)
    
    # Update collection metadata with last_updated timestamp
    try:
        # For newer ChromaDB versions, use modify method
        if hasattr(collection, 'modify'):
            collection.modify(metadata={"last_updated": datetime.utcnow().isoformat()})
        else:
            # Fallback: try to set metadata directly on the collection object
            collection.metadata = {"last_updated": datetime.utcnow().isoformat()}
    except Exception as e:
        print(f"Warning: Could not update collection metadata: {e}")
        # Continue without failing the entire operation
    
    return {"message": f"Indexing complete! Total chunks added: {document_counter}"}


@router.post("/update_nice")
def refresh_nice_index():
    """Fetch all NICE guidance and store it in ChromaDB."""
    try:
        indexed_docs = index_nice_knowledge()  # calls the API, processes, stores
        try:
            # Get the collection and update its last_updated metadata
            collection = chroma_client.get_collection(name="nice_knowledge")
            
            # Update collection metadata with last_updated timestamp
            try:
                # For newer ChromaDB versions, use modify method
                if hasattr(collection, 'modify'):
                    collection.modify(metadata={"last_updated": datetime.utcnow().isoformat()})
                else:
                    # Fallback: try to set metadata directly on the collection object
                    collection.metadata = {"last_updated": datetime.utcnow().isoformat()}
            except Exception as e:
                print(f"Warning: Could not update collection metadata: {e}")
                # Continue without failing the entire operation
                
            return {"message": f"Indexing complete! Total chunks added: {len(indexed_docs)}"}
        except Exception as e:
            return {"message": f"Indexing complete but failed to update metadata: {str(e)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))