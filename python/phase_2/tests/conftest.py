import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from phase_2.repositories.note_repo_class import NoteRepository
from phase_2.repositories.dataset_repo_class import DatasetRepository
from phase_2.services.note_service_class import NoteService
from phase_2.services.dataset_service_class import DatasetService
from phase_2.services.search_service_class import SearchService
from phase_2.api.main import create_app


@pytest.fixture
def note_repo(tmp_path):
    return NoteRepository(notes_home=tmp_path)


@pytest.fixture
def note_service(note_repo):
    return NoteService(note_repo)


@pytest.fixture
def dataset_repo(tmp_path):
    return DatasetRepository(notes_home=tmp_path)


@pytest.fixture
def dataset_service(dataset_repo):
    return DatasetService(dataset_repo)


@pytest.fixture
def search_service(note_service, dataset_service):
    return SearchService(note_service, dataset_service)


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    """
    FastAPI test client with isolated filesystem.
    """

    # Redirect home directory to temp path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    from phase_2.api.main import create_app

    app = create_app()
    return TestClient(app)