from pathlib import Path

from repositories.note_repo_class import NoteRepository
from repositories.dataset_repo_class import DatasetRepository
from services.note_service_class import NoteService
from services.dataset_service_class import DatasetService
from services.search_service_class import SearchService

DATA_DIR = Path("data")

note_repository = NoteRepository(DATA_DIR / "notes")
dataset_repository = DatasetRepository(DATA_DIR / "datasets")

note_service = NoteService(note_repository)
dataset_service = DatasetService(dataset_repository)
search_service = SearchService(note_service, dataset_service)


def get_note_service() -> NoteService:
    return note_service


def get_dataset_service() -> DatasetService:
    return dataset_service


def get_search_service() -> SearchService:
    return search_service