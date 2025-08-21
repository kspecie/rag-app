#app/main.py
import sys
import pysqlite3

# workaround for chromadb/sqlite3 before anything else that might import it
sys.modules["sqlite3"] = pysqlite3
sys.modules["_sqlite3"] = pysqlite3.dbapi2

import os
import logging
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from fastapi import Request
from typing import Optional

# Import the higher-level pipeline functions from app.core.pipeline
from app.core.pipeline import run_retrieval_and_generation_pipeline

# Import the documents router
from app.backend.api.documents import router as documents_router
from app.backend.api.summaries_store import router as summaries_store_router

#import collections router
from app.backend.api.collections import router as collections_router
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# --- API Key Setup ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY = os.getenv("API_KEY", "your-super-secret-default-key-DONT-USE-IN-PROD")
if API_KEY == "your-super-secret-default-key-DONT-USE-IN-PROD":
    logger.warning("API_KEY environment variable not set. Using default. Set API_KEY for production.")

async def get_api_key(request: Request, api_key: Optional[str] = Security(api_key_header)):
    # Skip API key validation for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return None
    
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
    "http://localhost:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Allow cookies, authorization headers, etc.
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],    # Allow all headers, including your custom 'X-API-Key'
)


app.include_router(documents_router, dependencies=[Depends(get_api_key)])
app.include_router(summaries_store_router, dependencies=[Depends(get_api_key)])
app.include_router(collections_router, dependencies=[Depends(get_api_key)])


@app.get("/")
async def read_root():
    """
    Root endpoint to confirm API is running.
    """
    return {"message": "Medical Conversation RAG API is running. Visit /docs for API documentation."}

# --- Pydantic model for summarization request body ---
class SummarizeRequest(BaseModel):
    text: str
    file_name: str | None = None

@app.post("/summaries/generate/", summary="Generate a clinical summary from conversation")
async def generate_clinical_summary(
    request: SummarizeRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Generates a clinical summary based on a provided transcribed medical conversation.
    It uses RAG to retrieve relevant context from uploaded documents before summarization.
    """
    transcribed_conversation = request.text

    if not transcribed_conversation.strip():
        raise HTTPException(status_code=400, detail="Transcribed conversation cannot be empty.")

    try:
        # --- Call the run_retrieval_and_generation_pipeline ---
        summary_result = run_retrieval_and_generation_pipeline(
            transcribed_conversation,
            summary_title=(request.file_name or None)
        )
        
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