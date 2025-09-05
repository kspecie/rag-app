#app/backend/api/documents.py
import os
import chromadb
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from typing import List, Dict, Any
from datetime import datetime

from app.core.pipeline import run_ingestion_pipeline, run_embedding_and_storage_pipeline

USER_UPLOAD_COLLECTION = "documents"
MIRIAD_COLLECTION = "miriad_knowledge"
NICE_COLLECTION = "nice_knowledge"

router = APIRouter(
    prefix="/documents", # All endpoints in this router will start with /documents
    tags=["Documents"], 
)

CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")

def get_client() -> chromadb.HttpClient:
    return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


@router.get("/")
def list_user_documents() -> List[Dict[str, Any]]:
    """
    List unique uploaded files in the 'documents' collection.
    Deduplicates by metadata['source'].
    """
    try:
        client = get_client()
        collection = client.get_or_create_collection(name=USER_UPLOAD_COLLECTION)
        results = collection.get(include=["metadatas"])

        file_map = {}

        for meta in results["metadatas"]:
            if not meta:
                continue
            source = meta.get("source", "unknown_source")
            upload_date = meta.get("upload_date")

            if source not in file_map:  # dedupe
                file_map[source] = {
                    "id": source,  # use filename as ID
                    "title": source,
                    "uploadDate": upload_date or "unknown",
                } 
            else:
                if file_map[source]["uploadDate"] == "unknown" and upload_date:
                    file_map[source]["uploadDate"] = upload_date


        return list(file_map.values())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Uploads new documents for ingestion into the RAG system.
    These documents will be chunked, embedded, and stored in ChromaDB.
    """
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded.")

    temp_dir = "./temp_uploaded_docs"
    os.makedirs(temp_dir, exist_ok=True)
    uploaded_file_paths = []

    try:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            uploaded_file_paths.append(file_path)
            print(f"File '{file.filename}' saved to '{file_path}'")

        # Store upload timestamp to add to metadata later
        upload_timestamp = datetime.utcnow().isoformat()
        
        chunks = run_ingestion_pipeline(temp_dir)
        if not chunks:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process documents into chunks.")

        # Add upload_date to all chunks before storing
        for chunk in chunks:
            if hasattr(chunk, 'metadata') and chunk.metadata:
                chunk.metadata['upload_date'] = upload_timestamp
            else:
                chunk.metadata = {'upload_date': upload_timestamp}

        run_embedding_and_storage_pipeline(chunks)

        return {"message": f"Successfully processed {len(files)} files and added them to ChromaDB."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing files: {str(e)}")
    finally:
        for file_path in uploaded_file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")

@router.get("/collections")
def list_collections():
    """
    List all available ChromaDB collections by name.
    """
    try:
        client = get_client()
        collections = client.list_collections()
        return [{"name": col.name} for col in collections]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{collection_name}")
def list_documents(collection_name: str) -> List[Dict[str, Any]]:
    """
    List unique uploaded files in a ChromaDB collection.
    Deduplicates by metadata['source'] and returns file-level info.
    """
    try:
        client = get_client()
        collection = client.get_or_create_collection(name=collection_name)
        results = collection.get(include=["metadatas"])

        file_map = {}

        for meta in results["metadatas"]:
            if not meta:
                continue
            source = meta.get("source", "unknown_source")
            upload_date = meta.get("upload_date")

            # Only keep first occurrence per source (dedupe)
            if source not in file_map:
                file_map[source] = {
                    "filename": source,
                    "upload_date": upload_date or "unknown",
                }

        return list(file_map.values())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/user")
def delete_user_upload_collection():
    """
    Delete an entire ChromaDB collection for user-uploaded files
    """
    try:
        client = get_client()
        client.delete_collection(name=USER_UPLOAD_COLLECTION)
        return {"message": f"Collection '{USER_UPLOAD_COLLECTION} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/miriad")
def delete_miriad_collection():
    """
    Delete the entire MiRIAD ChromaDB collection
    """
    try:
        client = get_client()
        client.delete_collection(name=MIRIAD_COLLECTION)
        return {"message": f"Collection '{MIRIAD_COLLECTION}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/nice")
def delete_nice_collection():
    """
    Delete the entire NICE ChromaDB collection
    """
    try:
        client = get_client()
        client.delete_collection(name=NICE_COLLECTION)
        return {"message": f"Collection '{NICE_COLLECTION}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))