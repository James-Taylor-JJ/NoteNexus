from datetime import datetime
from python.phase_2.models.note_class import Note
from python.phase_2.repositories.note_repo_class import NoteRepository
from python.phase_2.utilities.time_utilities_class import current_timestamp


class NoteService:
    def __init__(self, repository: NoteRepository):
        self.repository = repository

    def _parse_iso_datetime(self, value: str) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _in_date_range(
        self,
        value: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> bool:
        dt = self._parse_iso_datetime(value)
        if dt is None:
            return False

        start_dt = self._parse_iso_datetime(start_date) if start_date else None
        end_dt = self._parse_iso_datetime(end_date) if end_date else None

        if start_dt and dt < start_dt:
            return False
        if end_dt and dt > end_dt:
            return False
        return True

    def list_notes(self, include_archived: bool = False) -> list[Note]:
        notes = self.repository.load_all_notes()
        if include_archived:
            return notes
        return [note for note in notes if note.status != "archived"]

    def read_note(self, filename: str) -> Note | None:
        return self.repository.load_note(filename)

    def create_note(self, filename: str, title: str, author: str, content: str, tags=None) -> Note:
        if not filename.endswith((".md", ".note", ".txt")):
            filename += ".md"

        existing = self.repository.load_note(filename)
        if existing:
            raise ValueError(f"Note already exists: {filename}")

        timestamp = current_timestamp()
        note = Note(
            filename=filename,
            title=title.strip() or filename.rsplit(".", 1)[0],
            content=content,
            created=timestamp,
            modified=timestamp,
            author=author.strip() or "Unknown",
            tags=tags or [],
            status="active",
            archived_at=None,
        )
        self.repository.save_note(note)
        return note

    def edit_note(self, filename: str, new_content: str) -> Note | None:
        note = self.repository.load_note(filename)
        if not note:
            return None

        note.content = new_content
        note.modified = current_timestamp()
        self.repository.save_note(note)
        return note

    def delete_note(self, filename: str) -> bool:
        return self.repository.delete_note(filename)

    def archive_note(self, filename: str) -> Note | None:
        note = self.repository.load_note(filename)
        if not note:
            return None

        note.status = "archived"
        note.archived_at = current_timestamp()
        note.modified = current_timestamp()
        self.repository.save_note(note)
        return note

    def restore_note(self, filename: str) -> Note | None:
        note = self.repository.load_note(filename)
        if not note:
            return None

        note.status = "active"
        note.archived_at = None
        note.modified = current_timestamp()
        self.repository.save_note(note)
        return note

    def list_archived_notes(self) -> list[Note]:
        return [note for note in self.repository.load_all_notes() if note.status == "archived"]

    def filter_notes_by_date(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        date_field: str = "modified",
        include_archived: bool = False,
    ) -> list[Note]:
        notes = self.list_notes(include_archived=include_archived)

        valid_fields = {"created", "modified", "archived_at"}
        if date_field not in valid_fields:
            raise ValueError(f"Invalid date field: {date_field}")

        results = []
        for note in notes:
            value = getattr(note, date_field, None)
            if value and self._in_date_range(value, start_date, end_date):
                results.append(note)

        return results