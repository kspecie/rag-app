from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid

# Reuse the SQLAlchemy setup and model from scripts.save_summary
try:
    from scripts.save_summary import SessionLocal, Summary
except Exception as e:
    # Fallback error to make it explicit in API responses if DB isn't configured
    SessionLocal = None
    Summary = None

router = APIRouter(
    prefix="/summaries",
    tags=["Summaries"],
)


class SaveSummaryRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = "Clinical Summary"
    content: str


@router.post("/save/")
def save_or_update_summary(payload: SaveSummaryRequest):
    if SessionLocal is None or Summary is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database is not configured correctly."
        )

    db = SessionLocal()
    try:
        if payload.id:
            existing = db.query(Summary).filter(Summary.id == payload.id).first()
            if existing:
                if payload.title:
                    existing.title = payload.title
                existing.content = payload.content
                db.commit()
                return {"id": existing.id, "status": "updated"}
            # If ID provided but not found, create new with provided ID
            new_id = payload.id
        else:
            new_id = str(uuid.uuid4())

        new_summary = Summary(
            id=new_id,
            title=payload.title or "Clinical Summary",
            content=payload.content,
        )
        db.add(new_summary)
        db.commit()
        return {"id": new_id, "status": "created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save summary: {e}"
        )
    finally:
        db.close()

@router.get("/get/{summary_id}")
def get_summary(summary_id: str):
    if SessionLocal is None or Summary is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database is not configured correctly."
        )
    db = SessionLocal()
    try:
        found = db.query(Summary).filter(Summary.id == summary_id).first()
        if not found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")
        return {"id": found.id, "title": found.title, "content": found.content}
    finally:
        db.close()

@router.get("/list/")
def list_summaries(limit: int = 10):
    if SessionLocal is None or Summary is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database is not configured correctly."
        )
    db = SessionLocal()
    try:
        # Simple listing in insertion order if DB preserves it; for production add created_at and order by desc
        items = db.query(Summary).limit(limit).all()
        return [{"id": s.id, "title": s.title, "content": s.content} for s in items]
    finally:
        db.close()


