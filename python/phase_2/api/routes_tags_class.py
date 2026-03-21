from fastapi import APIRouter, Depends

from api.deps import get_search_service
from api.schemas import TagListResponse
from services.search_service_class import SearchService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=TagListResponse)
def list_tags(service: SearchService = Depends(get_search_service)):
    return TagListResponse(tags=service.get_all_tags())