from fastapi import APIRouter, HTTPException, status
from app.core.pipeline import run_retrieval_and_generation_pipeline 

router = APIRouter(
    prefix="/summaries", # All endpoints in this router will start with /summaries
    tags=["Summaries"], 
)

@router.post("/generate/")
async def generate_summary_endpoint(transcribed_conversation: str):
    """
    Generates a clinical summary from a transcribed medical conversation
    using the RAG system.
    """
    if not transcribed_conversation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transcribed conversation cannot be empty.")

    summary = run_retrieval_and_generation_pipeline(transcribed_conversation)
    print("summary", summary)
    if summary is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate summary.")

    return {"summary": summary}