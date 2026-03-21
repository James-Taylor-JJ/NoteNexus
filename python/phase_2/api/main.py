from fastapi import FastAPI

from phase_2.api.routes.routes_notes_class import router as notes_router, register_note_routes
from phase_2.api.routes.routes_datasets_class import router as datasets_router, register_dataset_routes
from phase_2.api.routes.routes_search_class import router as search_router, register_search_routes

from phase_2.repositories.note_repo_class import NoteRepository
from phase_2.repositories.dataset_repo_class import DatasetRepository

from phase_2.services.note_service_class import NoteService
from phase_2.services.dataset_service_class import DatasetService
from phase_2.services.search_service_class import SearchService


def create_app() -> FastAPI:
    app = FastAPI(title="NoteNexus API", version="0.1.0")

    note_repository = NoteRepository()
    dataset_repository = DatasetRepository()

    note_service = NoteService(note_repository)
    dataset_service = DatasetService(dataset_repository)
    search_service = SearchService(note_service, dataset_service)

    register_note_routes(notes_router, note_service)
    register_dataset_routes(datasets_router, dataset_service)
    register_search_routes(search_router, search_service)

    app.include_router(notes_router)
    app.include_router(datasets_router)
    app.include_router(search_router)

    @app.get("/")
    def root():
        return {"message": "NoteNexus API is running"}

    return app


app = create_app()