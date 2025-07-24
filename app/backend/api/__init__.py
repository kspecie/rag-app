# app/backend/api/__init__.py (or app/backend/api/router.py)
from fastapi import APIRouter

# Import your specific endpoint routers
from . import documents # Assuming documents.py is in the same directory
from . import summaries # Assuming summaries.py is in the same directory

# Create a main API router that includes other routers
api_router = APIRouter()

# Include the specific routers, potentially with prefixes
api_router.include_router(documents.router) # documents.router should have prefix="/documents" in its own file
api_router.include_router(summaries.router) # summaries.router should have prefix="/summaries" in its own file

# Make 'router' available for app.server.py to import
router = api_router