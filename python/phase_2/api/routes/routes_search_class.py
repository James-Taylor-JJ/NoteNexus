from fastapi import APIRouter, Depends, Query

from phase_2.api.deps import get_search_service
from phase_2.api.schemas import SearchResultResponse
from phase_2.services.search_service_class import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[SearchResultResponse])
def search_all(
    q: str = Query(..., min_length=1),
    include_archived: bool = False,
    service: SearchService = Depends(get_search_service),
):
    return service.search_all(q, include_archived=include_archived)


@router.get("/by-tag", response_model=list[SearchResultResponse])
def search_all_by_tag(
    tag: str = Query(..., min_length=1),
    include_archived: bool = False,
    service: SearchService = Depends(get_search_service),
):
    return service.search_all_by_tag(tag, include_archived=include_archived)