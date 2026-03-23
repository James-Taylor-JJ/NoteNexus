from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from python.phase_2.api.routes.routes_notes_class import build_notes_router
from python.phase_2.api.routes.routes_datasets_class import build_datasets_router
from python.phase_2.api.routes.routes_search_class import build_search_router

from python.phase_2.repositories.note_repo_class import NoteRepository
from python.phase_2.repositories.dataset_repo_class import DatasetRepository

from python.phase_2.services.note_service_class import NoteService
from python.phase_2.services.dataset_service_class import DatasetService
from python.phase_2.services.search_service_class import SearchService


def create_app() -> FastAPI:
    app = FastAPI(title="NoteNexus API", version="0.1.0")

    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5500","http://127.0.0.1:5500"], allow_credentials = True, allow_methods = ["*"], allow_headers = ["*"])

    note_repository = NoteRepository()
    dataset_repository = DatasetRepository()

    note_service = NoteService(note_repository)
    dataset_service = DatasetService(dataset_repository)
    search_service = SearchService(note_service, dataset_service)

    app.include_router(build_notes_router(note_service))
    app.include_router(build_datasets_router(dataset_service))
    app.include_router(build_search_router(search_service))

    @app.get("/")
    def root():
        return {"message": "NoteNexus API is running"}

    return app


app = create_app()