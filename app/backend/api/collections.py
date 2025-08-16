# backend/api/collections.py

import os
import subprocess
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import sys

# Define your Pydantic model and APIRouter as before
class CollectionInfo(BaseModel):
    name: str
    last_updated: Optional[datetime] = None

router = APIRouter(
    prefix="/collections",  # Add this prefix
    tags=["Collections"],
)

collection_metadata = {
    "Miriad Knowledge": {
        "last_updated": datetime(2023, 10, 26, 9, 0, 0),
    },
    "Nice Knowledge": {
        "last_updated": datetime(2024, 8, 15, 12, 0, 0),
    },
    "My Documents": {
        "last_updated": datetime(2024, 8, 16, 17, 0, 0),
    },
}

class CollectionAction(BaseModel):
    collection_name: str

@router.get("/{collection_name}", response_model=CollectionInfo)
async def get_collection_info(collection_name: str):
    if collection_name not in collection_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection '{collection_name}' not found."
        )
    last_updated = collection_metadata[collection_name]["last_updated"]

    if last_updated is None:
        return {
            "name": collection_name,
            "last_updated": None
        }
    
    return {
        "name": collection_name,
        "last_updated": collection_metadata[collection_name]["last_updated"],
    }

@router.post("/{action}")
async def manage_collection(action: str, collection_action: CollectionAction):
    if action not in ["delete", "index"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'delete' or 'index'."
        )

    if action == "index" and collection_action.collection_name == "My Documents":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'My Documents' collection can only be indexed via the file upload endpoint."
        )

    try:
        command = [
            sys.executable,
            os.path.abspath("scripts/manage_collections.py"),
            action,
            collection_action.collection_name,
        ]

        result = subprocess.run(command, capture_output=True, text=True, check=True)

        if action == "index":
            collection_metadata[collection_action.collection_name]["last_updated"] = datetime.now()
        
        # New: Remove the collection from our metadata on successful deletion
        if action == "delete" and collection_action.collection_name in collection_metadata:
            collection_metadata[collection_action.collection_name]["last_updated"] = None

        return {
            "message": f"Successfully executed '{action}' for collection '{collection_action.collection_name}'.",
            "details": result.stdout.strip()
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Script failed with error: {e.stderr.strip()}"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The 'manage_collections.py' script was not found. Check the file path."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )