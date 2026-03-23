from typing import List, Dict, Any, Optional

from python.phase_2.services.note_service_class import NoteService
from python.phase_2.services.dataset_service_class import DatasetService


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

    def get_all_note_tags(self) -> List[str]:
        tags = set()
        notes = self.note_service.list_notes(include_archived=True)

        for note in notes:
            for tag in note.tags:
                cleaned = tag.strip()
                if cleaned:
                    tags.add(cleaned)

        return sorted(tags, key=str.lower)

    def get_all_dataset_tags(self) -> List[str]:
        tags = set()
        datasets = self.dataset_service.list_datasets()

        for dataset in datasets:
            for tag in dataset.tags:
                cleaned = tag.strip()
                if cleaned:
                    tags.add(cleaned)

        return sorted(tags, key=str.lower)

    def get_all_tags(self) -> List[str]:
        all_tags = set(self.get_all_note_tags()) | set(self.get_all_dataset_tags())
        return sorted(all_tags, key=str.lower)

    def search_notes(self, query: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        query = query.strip().lower()
        if not query:
            return []

        results = []
        notes = self.note_service.list_notes(include_archived=include_archived)

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
                        "status": note.status,
                        "archived_at": note.archived_at,
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

    def search_all(self, query: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        query = query.strip()
        if not query:
            return []

        note_results = self.search_notes(query, include_archived=include_archived)
        dataset_results = self.search_datasets(query)

        combined = note_results + dataset_results
        combined.sort(key=lambda item: (item["type"], item["title"].lower()))
        return combined

    def search_notes_by_tag(self, tag: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        tag = tag.strip().lower()
        if not tag:
            return []

        results = []
        notes = self.note_service.list_notes(include_archived=include_archived)

        for note in notes:
            normalized_tags = [t.strip().lower() for t in note.tags]
            if tag in normalized_tags:
                results.append(
                    {
                        "type": "note",
                        "id": note.filename,
                        "title": note.title,
                        "author": note.author,
                        "created": note.created,
                        "modified": note.modified,
                        "tags": note.tags,
                        "status": note.status,
                        "archived_at": note.archived_at,
                    }
                )

        return results

    def search_datasets_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        tag = tag.strip().lower()
        if not tag:
            return []

        results = []
        datasets = self.dataset_service.list_datasets()

        for dataset in datasets:
            normalized_tags = [t.strip().lower() for t in dataset.tags]
            if tag in normalized_tags:
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

    def search_all_by_tag(self, tag: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        tag = tag.strip()
        if not tag:
            return []

        note_results = self.search_notes_by_tag(tag, include_archived=include_archived)
        dataset_results = self.search_datasets_by_tag(tag)

        combined = note_results + dataset_results
        combined.sort(key=lambda item: (item["type"], item["title"].lower()))
        return combined

    def filter_notes_by_date(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        date_field: str = "modified",
        include_archived: bool = False,
    ) -> List[Dict[str, Any]]:
        notes = self.note_service.filter_notes_by_date(
            start_date=start_date,
            end_date=end_date,
            date_field=date_field,
            include_archived=include_archived,
        )

        return [
            {
                "type": "note",
                "id": note.filename,
                "title": note.title,
                "author": note.author,
                "created": note.created,
                "modified": note.modified,
                "tags": note.tags,
                "status": note.status,
                "archived_at": note.archived_at,
            }
            for note in notes
        ]