import pytest

from repositories.note_repo_class import NoteRepository
from repositories.dataset_repo_class import DatasetRepository
from services.note_service_class import NoteService
from services.dataset_service_class import DatasetService
from services.search_service_class import SearchService


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