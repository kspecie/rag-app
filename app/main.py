import sys
import pysqlite3

# workaround for chromadb/sqlite3 before anything else that might import it
sys.modules["sqlite3"] = pysqlite3
sys.modules["_sqlite3"] = pysqlite3.dbapi2

import os
import logging
import shutil     # Added for file handling
import tempfile   # Added for temporary directory creation (pre embedding)
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from typing import List

# Import the higher-level pipeline functions from app.core.pipeline
from app.core.pipeline import run_ingestion_pipeline, run_embedding_and_storage_pipeline, run_retrieval_and_generation_pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# --- API Key Setup ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
API_KEY = os.getenv("API_KEY", "your-super-secret-default-key-DONT-USE-IN-PROD")
if API_KEY == "your-super-secret-default-key-DONT-USE-IN-PROD":
    logger.warning("API_KEY environment variable not set. Using default. Set API_KEY for production.")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Could not validate credentials - Invalid API Key")

# --- FastAPI App Definition ---
app = FastAPI(
    title="Clinical Summaries RAG API",
    description="API for RAG (Retrieval-Augmented Generation) on medical conversations and documents.",
    version="0.1.0",
)

# Configure CORS
origins = [
    "http://localhost", 
    "http://localhost:5173", # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Allow cookies, authorization headers, etc.
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],    # Allow all headers, including your custom 'X-API-Key'
)

@app.get("/")
async def read_root():
    """
    Root endpoint to confirm API is running.
    This endpoint can be public if you want, or you can add security to it too.
    """
    return {"message": "Medical Conversation RAG API is running. Visit /docs for API documentation."}

@app.post("/documents/upload/", summary="Upload documents to ChromaDB")
async def upload_documents(files: List[UploadFile] = File(...), api_key: str = Depends(get_api_key)):
    """
    Uploads document files (e.g., .txt, .pdf) to be processed and stored
    in ChromaDB for retrieval.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload.")

    processed_count = 0
    temp_dir = None
    try:
        # Create a temporary directory to save uploaded files
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Saving uploaded files to temporary directory: {temp_dir}")
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            # Use await file.read() for async handling of UploadFile content
            contents = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            logger.info(f"Saved {file.filename} to {file_path}")

        # --- Call the run_ingestion_pipeline from app.core.pipeline ---
        # This function expects a directory path
        documents_processed = run_ingestion_pipeline(temp_dir)
        
        # --- Then call the embedding and storage pipeline with the results
        if documents_processed:
            run_embedding_and_storage_pipeline(documents_processed)
            processed_count = len(documents_processed) # Count based on what was processed
        else:
            logger.warning("No documents processed by ingestion pipeline.")


        return JSONResponse(
            status_code=200,
            content={"message": f"Successfully processed {processed_count} files and added them to ChromaDB."}
        )
    except Exception as e:
        logger.error(f"Error during document upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process documents: {str(e)}"
        )
    finally:
        # Clean up the temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")

@app.post("/summaries/generate/", summary="Generate a clinical summary from conversation")
async def generate_clinical_summary(
    transcribed_conversation: str = Query(
        ...,
        description="The transcribed medical conversation to summarize."
    ),
    api_key: str = Depends(get_api_key)
):
    """
    Generates a clinical summary based on a provided transcribed medical conversation.
    It uses RAG to retrieve relevant context from uploaded documents before summarization.
    """
    if not transcribed_conversation:
        raise HTTPException(status_code=400, detail="Transcribed conversation cannot be empty.")

    try:
        # --- Call the run_retrieval_and_generation_pipeline ---
        summary_result = run_retrieval_and_generation_pipeline(transcribed_conversation)
        
        if summary_result is None:
            raise HTTPException(
                status_code=404,
                detail="Could not generate summary (e.g., no relevant context found or TGI issue)."
            )

        return JSONResponse(
            status_code=200,
            content={"summary": summary_result}
        )
    except Exception as e:
        logger.error(f"Error during summary generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )