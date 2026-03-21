from pathlib import Path
from typing import Optional
from phase_2.models.note_class import Note


class NoteRepository:
    def __init__(self, notes_home: Optional[Path] = None):
        self.notes_home = notes_home or (Path.home() / ".notes")
        self.notes_dir = self.notes_home / "notes"

    def ensure_notes_dir(self) -> Path:
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        return self.notes_dir

    def get_note_files(self) -> list[Path]:
        self.ensure_notes_dir()
        note_files = []
        note_files.extend(self.notes_dir.glob("*.md"))
        note_files.extend(self.notes_dir.glob("*.note"))
        note_files.extend(self.notes_dir.glob("*.txt"))
        return sorted(note_files)

    def parse_yaml_header(self, file_path: Path) -> dict:
        metadata = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if lines and lines[0].strip() == "---":
                for line in lines[1:]:
                    line = line.strip()
                    if line == "---":
                        break
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
        except Exception as e:
            metadata["error"] = str(e)

        return metadata

    def read_note_content(self, file_path: Path) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        content_start = 0
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    content_start = i + 1
                    break

        return "".join(lines[content_start:]).strip()

    def write_note_file(self, file_path: Path, metadata: dict, content: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            for key, value in metadata.items():
                if key == "tags" and isinstance(value, list):
                    f.write(f"{key}: [{', '.join(value)}]\n")
                else:
                    f.write(f"{key}: {value}\n")
            f.write("---\n\n")
            f.write(content.strip() + "\n")

    def load_note(self, filename: str) -> Optional[Note]:
        file_path = self.notes_dir / filename
        if not file_path.exists():
            return None

        metadata = self.parse_yaml_header(file_path)
        content = self.read_note_content(file_path)
        

        tags = metadata.get("tags", "")
        if isinstance(tags, str) and tags.startswith("[") and tags.endswith("]"):
            tags = [tag.strip() for tag in tags[1:-1].split(",") if tag.strip()]
        elif not tags:
            tags = []

        return Note(
            filename=file_path.name,
            title=metadata.get("title", file_path.stem),
            content=content,
            created=metadata.get("created", ""),
            modified=metadata.get("modified", ""),
            author=metadata.get("author"),
            tags=tags,
            status=metadata.get("status"),
            priority=int(metadata["priority"]) if metadata.get("priority") else None,
            archived_at = metadata.get("archived_at"),
        )

    def load_all_notes(self) -> list[Note]:
        notes = []
        for path in self.get_note_files():
            note = self.load_note(path.name)
            if note:
                notes.append(note)
        return notes

    def save_note(self, note: Note) -> None:
        self.ensure_notes_dir()
        file_path = self.notes_dir / note.filename
        metadata = {
            "title": note.title,
            "author": note.author or "Unknown",
            "created": note.created,
            "modified": note.modified,
            "tags": note.tags,
        }
        if note.status:
            metadata["status"] = note.status
        if note.priority is not None:
            metadata["priority"] = note.priority
        if note.archived_at:
            metadata["archived_at"] = note.archived_at

        self.write_note_file(file_path, metadata, note.content)

    def delete_note(self, filename: str) -> bool:
        file_path = self.notes_dir / filename
        if not file_path.exists():
            return False
        file_path.unlink()
        return True