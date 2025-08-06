#app/backend/api/documents.py
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List

from app.core.pipeline import run_ingestion_pipeline, run_embedding_and_storage_pipeline

router = APIRouter(
    prefix="/documents", # All endpoints in this router will start with /documents
    tags=["Documents"], # For grouping in Swagger UI
)

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

        chunks = run_ingestion_pipeline(temp_dir)
        if not chunks:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process documents into chunks.")

        run_embedding_and_storage_pipeline(chunks)

        return {"message": f"Successfully processed {len(files)} files and added them to ChromaDB."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing files: {str(e)}")
    finally:
        for file_path in uploaded_file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")

# import os
# import shutil
# from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
# from typing import List
# from pydantic import BaseModel
# import chromadb
# from chromadb.config import Settings

# from app.core.pipeline import run_ingestion_pipeline, run_embedding_and_storage_pipeline

# router = APIRouter(
#     prefix="/documents",
#     tags=["Documents"],
# )

# class DeleteRequest(BaseModel):
#     ids: List[str]

# @router.post("/upload/")
# async def upload_documents(files: List[UploadFile] = File(...)):
#     """
#     Uploads new documents for ingestion into the RAG system.
#     These documents will be chunked, embedded, and stored in ChromaDB.
#     """
#     if not files:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded.")

#     temp_dir = "./temp_uploaded_docs"
#     os.makedirs(temp_dir, exist_ok=True)
#     uploaded_file_paths = []

#     try:
#         for file in files:
#             file_path = os.path.join(temp_dir, file.filename)
#             with open(file_path, "wb") as buffer:
#                 buffer.write(await file.read())
#             uploaded_file_paths.append(file_path)
#             print(f"File '{file.filename}' saved to '{file_path}'")

#         chunks = run_ingestion_pipeline(temp_dir)
#         if not chunks:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process documents into chunks.")

#         run_embedding_and_storage_pipeline(chunks)

#         return {"message": f"Successfully processed {len(files)} files and added them to ChromaDB."}
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing files: {str(e)}")
#     finally:
#         for file_path in uploaded_file_paths:
#             if os.path.exists(file_path):
#                 os.remove(file_path)
#         if os.path.exists(temp_dir):
#             os.rmdir(temp_dir)
#             print(f"Cleaned up temporary directory: {temp_dir}")

# @router.get("/list/")
# async def list_documents():
#     """
#     List all documents currently stored in ChromaDB.
#     Returns unique document sources and their chunk counts.
#     """
#     try:
#         # Initialize ChromaDB client
#         persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
#         client = chromadb.PersistentClient(path=persist_dir)
        
#         try:
#             collection = client.get_collection(name="rag_documents")
#         except Exception:
#             # Collection doesn't exist
#             return {"documents": []}
        
#         # Get all documents
#         all_docs = collection.get(include=["metadatas"])
        
#         # Group by source (filename)
#         document_map = {}
#         for metadata in all_docs.get("metadatas", []):
#             source = metadata.get("source", "Unknown")
#             if source not in document_map:
#                 document_map[source] = {
#                     "id": source,  # Use filename as ID
#                     "title": os.path.basename(source),
#                     "chunk_count": 0
#                 }
#             document_map[source]["chunk_count"] += 1
        
#         return {"documents": list(document_map.values())}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

# @router.delete("/delete/")
# async def delete_documents(request: DeleteRequest):
#     """
#     Delete documents from ChromaDB by their source filenames.
#     """
#     try:
#         # Initialize ChromaDB client
#         persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
#         client = chromadb.PersistentClient(path=persist_dir)
        
#         try:
#             collection = client.get_collection(name="rag_documents")
#         except Exception:
#             raise HTTPException(status_code=404, detail="No documents found to delete.")
        
#         total_deleted = 0
        
#         # Debug: Show all current documents
#         all_docs = collection.get(include=["metadatas", "ids"])
#         print("[DEBUG] All documents currently in collection:")
#         for i, metadata in enumerate(all_docs.get("metadatas", [])):
#             print(f"  {i}: {metadata.get('source')}")
        
#         # Delete documents by source filename
#         for doc_id in request.ids:
#             print(f"[DEBUG] Searching for documents with source = {doc_id}")
            
#             # Find all chunks with this source
#             results = collection.get(
#                 where={"source": doc_id},
#                 include=["ids"]
#             )
            
#             ids_to_delete = results.get("ids", [])
#             print(f"[DEBUG] Found {len(ids_to_delete)} chunks to delete for {doc_id}")
            
#             if ids_to_delete:
#                 collection.delete(ids=ids_to_delete)
#                 total_deleted += len(ids_to_delete)
#                 print(f"[DEBUG] Deleted {len(ids_to_delete)} chunks for {doc_id}")
        
#         if total_deleted == 0:
#             raise HTTPException(status_code=404, detail="No matching documents found to delete.")
        
#         return {"message": f"Deleted {total_deleted} chunks for {len(request.ids)} documents."}
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"[ERROR] Error deleting documents: {e}")
#         raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")

# @router.delete("/delete-all/")
# async def delete_all_documents():
#     """
#     Delete all documents from ChromaDB by removing the entire persistence directory.
#     """
#     try:
#         persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        
#         if os.path.exists(persist_dir):
#             shutil.rmtree(persist_dir)
#             print(f"Deleted ChromaDB persistence directory: {persist_dir}")
#             return {"message": "Successfully deleted all documents from ChromaDB."}
#         else:
#             raise HTTPException(status_code=404, detail="No documents to delete.")
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"[ERROR] Error deleting all documents: {e}")
#         raise HTTPException(status_code=500, detail=f"Error deleting all documents: {str(e)}")