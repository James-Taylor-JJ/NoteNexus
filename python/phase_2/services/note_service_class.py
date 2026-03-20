from datetime import datetime, timezone
from models.note_class import Note
from repositories.note_repo_class import NoteRepository


class NoteService:
    def __init__(self, repository: NoteRepository):
        self.repository = repository

    def current_timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def list_notes(self) -> list[Note]:
        return self.repository.load_all_notes()

    def read_note(self, filename: str) -> Note | None:
        return self.repository.load_note(filename)

    def create_note(self, filename: str, title: str, author: str, content: str, tags=None) -> Note:
        if not filename.endswith((".md", ".note", ".txt")):
            filename += ".md"

        existing = self.repository.load_note(filename)
        if existing:
            raise ValueError(f"Note already exists: {filename}")

        timestamp = self.current_timestamp()
        note = Note(
            filename=filename,
            title=title.strip() or filename.rsplit(".", 1)[0],
            content=content,
            created=timestamp,
            modified=timestamp,
            author=author.strip() or "Unknown",
            tags=tags or [],
        )
        self.repository.save_note(note)
        return note

    def edit_note(self, filename: str, new_content: str) -> Note | None:
        note = self.repository.load_note(filename)
        if not note:
            return None

        note.content = new_content
        note.modified = self.current_timestamp()
        self.repository.save_note(note)
        return note

    def delete_note(self, filename: str) -> bool:
        return self.repository.delete_note(filename)