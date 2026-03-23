from typing import Optional

from fastapi import APIRouter, Query

from python.phase_2.services.search_service_class import SearchService


def build_search_router(search_service: SearchService) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["search"])

    @router.get("/search")
    def search_all(q: str = Query(...), include_archived: bool = False):
        return search_service.search_all(q, include_archived=include_archived)

    @router.get("/search/notes")
    def search_notes(q: str = Query(...), include_archived: bool = False):
        return search_service.search_notes(q, include_archived=include_archived)

    @router.get("/search/datasets")
    def search_datasets(q: str = Query(...)):
        return search_service.search_datasets(q)

    @router.get("/search/tag/{tag}")
    def search_all_by_tag(tag: str, include_archived: bool = False):
        return search_service.search_all_by_tag(tag, include_archived=include_archived)

    @router.get("/tags")
    def get_all_tags():
        return {"tags": search_service.get_all_tags()}

    @router.get("/tags/notes")
    def get_note_tags():
        return {"tags": search_service.get_all_note_tags()}

    @router.get("/tags/datasets")
    def get_dataset_tags():
        return {"tags": search_service.get_all_dataset_tags()}

    @router.get("/notes/filter/by-date")
    def filter_notes_by_date(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date_field: str = "modified",
        include_archived: bool = False,
    ):
        return search_service.filter_notes_by_date(
            start_date=start_date,
            end_date=end_date,
            date_field=date_field,
            include_archived=include_archived,
        )

    return router
