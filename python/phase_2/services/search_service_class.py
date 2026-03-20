from typing import List, Dict, Any, Optional

from services.note_service_class import NoteService
from services.dataset_service_class import DatasetService


class SearchService:
    def __init__(self, note_service: NoteService, dataset_service: DatasetService):
        self.note_service = note_service
        self.dataset_service = dataset_service

    def _matches_text(self, query: str, value: Optional[str]) -> bool:
        if not value:
            return False
        return query in value.lower()

    def _matches_tags(self, query: str, tags: List[str]) -> bool:
        return any(query in tag.lower() for tag in tags)

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        query = query.strip().lower()
        if not query:
            return []

        results = []
        notes = self.note_service.list_notes()

        for note in notes:
            if (
                self._matches_text(query, note.filename)
                or self._matches_text(query, note.title)
                or self._matches_text(query, note.author)
                or self._matches_text(query, note.content)
                or self._matches_tags(query, note.tags)
            ):
                results.append(
                    {
                        "type": "note",
                        "id": note.filename,
                        "title": note.title,
                        "author": note.author,
                        "created": note.created,
                        "modified": note.modified,
                        "tags": note.tags,
                    }
                )

        return results

    def search_datasets(self, query: str) -> List[Dict[str, Any]]:
        query = query.strip().lower()
        if not query:
            return []

        results = []
        datasets = self.dataset_service.list_datasets()

        for dataset in datasets:
            schema_text = " ".join(
                str(column.get("name", "")) for column in dataset.schema
            )

            if (
                self._matches_text(query, dataset.filename)
                or self._matches_text(query, dataset.title)
                or self._matches_text(query, dataset.author)
                or self._matches_text(query, dataset.format)
                or self._matches_text(query, schema_text)
                or self._matches_tags(query, dataset.tags)
            ):
                results.append(
                    {
                        "type": "dataset",
                        "id": dataset.filename,
                        "title": dataset.title,
                        "author": dataset.author,
                        "created": dataset.created,
                        "modified": dataset.modified,
                        "tags": dataset.tags,
                        "format": dataset.format,
                        "row_count": dataset.row_count,
                    }
                )

        return results

    def search_all(self, query: str) -> List[Dict[str, Any]]:
        query = query.strip()
        if not query:
            return []

        note_results = self.search_notes(query)
        dataset_results = self.search_datasets(query)

        combined = note_results + dataset_results
        combined.sort(key=lambda item: (item["type"], item["title"].lower()))
        return combined