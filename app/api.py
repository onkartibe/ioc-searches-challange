from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from .models import SubmitRequest, SubmitResponse, DataResponse
from .service import DataService
from .repository import InMemoryRepository

router = APIRouter()

repo = InMemoryRepository()
service = DataService(repo)

def get_service() -> DataService:
    """
    Dependency injector for DataService.
    """
    return service

@router.post("/submit", response_model=SubmitResponse, status_code=201)
def submit(
    req: SubmitRequest,
    service: DataService = Depends(get_service)
):
    """
    Submit a new data entry.
    """
    try:
        entry_id = service.submit(req)
        return SubmitResponse(id=entry_id)
    except ValueError as e:
        msg = str(e)
        if "Duplicate entry" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=422, detail=msg)

@router.get("/data", response_model=DataResponse)
def get_data(
    q: str = Query(..., alias="q", description="Value to search for"),
    tags: Optional[str] = Query(None, alias="tags", description="Comma-separated tags"),
    limit: int = Query(10, alias="limit", ge=1, le=100, description="Max results"),
    service: DataService = Depends(get_service)
):
    """
    Retrieve data entries matching the query and tags.
    """
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    entries = service.search(q, tag_list, limit)
    return DataResponse(
        data=[
            {"value": e.value, "tags": e.tags, "type": e.type}
            for e in entries
        ]
    )