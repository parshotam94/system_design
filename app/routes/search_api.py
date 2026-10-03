from fastapi import APIRouter, Query
from app.services.search_service import search_service

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get("")
def search_concepts(q: str = Query(..., min_length=1, description="Search query term")):
    results = search_service.search(q, limit=12)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }
