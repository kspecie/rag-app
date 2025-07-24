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