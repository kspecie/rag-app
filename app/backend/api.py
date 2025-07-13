from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
import os
from dotenv import load_dotenv
from app.main import run_ingestion_pipeline, run_embedding_and_storage_pipeline, run_retrieval_and_generation_pipeline

load_dotenv()

router = APIRouter()

RAW_DATA_DIRECTORY = os.getenv("RAW_DATA_DIRECTORY", "/rag_app/data/raw_data")

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Endpoint to handle document uploads and trigger the ingestion and embedding pipelines.
    """
    save_path = os.path.join(RAW_DATA_DIRECTORY, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"File saved to {save_path}")

    chunks = run_ingestion_pipeline(RAW_DATA_DIRECTORY)
    if not chunks:
        return JSONResponse(status_code=400, content={"message": "Failed to process uploaded document."})

    run_embedding_and_storage_pipeline(chunks)

    return {"message": f"Document '{file.filename}' ingested and embedded successfully."}

@router.post("/summarize")
async def summarize_conversation(conversation: str = Form(...)):
    """
    Endpoint to accept a conversation and return a generated summary using the RAG pipeline.
    """
    summary = run_retrieval_and_generation_pipeline(conversation)
    if not summary:
        return JSONResponse(status_code=500, content={"message": "Failed to generate summary."})

    return {"summary": summary}
