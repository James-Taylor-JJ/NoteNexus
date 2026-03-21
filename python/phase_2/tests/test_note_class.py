import pytest
from pathlib import Path

from phase_2.models.note_class import Note
from phase_2.repositories.note_repo_class import NoteRepository


def make_sample_note(
    filename="test-note.md",
    title="Test Note",
    content="This is a test note.",
    created="2026-03-20T10:00:00Z",
    modified="2026-03-20T10:00:00Z",
    author="James",
    tags=None,
    status="active",
    priority=1,
    archived_at=None,
):
    return Note(
        filename=filename,
        title=title,
        content=content,
        created=created,
        modified=modified,
        author=author,
        tags=tags or ["test", "notes"],
        status=status,
        priority=priority,
        archived_at=archived_at,
    )


def test_ensure_notes_dir_creates_directory(tmp_path):
    repo = NoteRepository(notes_home=tmp_path)

    notes_dir = repo.ensure_notes_dir()

    assert notes_dir.exists()
    assert notes_dir.is_dir()
    assert notes_dir == tmp_path / "notes"


def test_save_note_creates_file(tmp_path):
    repo = NoteRepository(notes_home=tmp_path)
    note = make_sample_note()

    repo.save_note(note)

    saved_file = tmp_path / "notes" / note.filename
    assert saved_file.exists()
    assert saved_file.is_file()


def test_load_note_returns_saved_note(tmp_path):
    repo = NoteRepository(notes_home=tmp_path)
    note = make_sample_note()

    repo.save_note(note)
    loaded = repo.load_note(note.filename)

    assert loaded is not None
    assert loaded.filename == note.filename
    assert loaded.title == note.title
    assert loaded.content == note.content
    assert loaded.created == note.created
    assert loaded.modified == note.modified
    assert loaded.author == note.author
    assert loaded.tags == note.tags
    assert loaded.status == note.status
    assert loaded.priority == note.priority
    assert loaded.archived_at == note.archived_at


def test_load_note_returns_none_for_missing_file(tmp_path):
    repo = NoteRepository(notes_home=tmp_path)

    loaded = repo.load_note("missing-note.md")

    assert loaded is None


def test_load_all_notes_returns_all_saved_notes(tmp_path):
    repo = NoteRepository(notes_home=tmp_path)

    note1 = make_sample_note(filename="one.md", title="One")
    note2 = make_sample_note(filename="two.md", title="Two")
    repo.save_note(note1)
    repo.save_note(note2)

    notes = repo.load_all_notes()
    filenames = [note.filename for note in notes]

    assert len(notes) == 2
    assert "one.md" in filenames
    assert "two.md" in filenames


def test_delete_note_removes_file(tmp_path):
    repo = NoteRepository(notes_home=tmp_path)
    note = make_sample_note()

    repo.save_note(note)
    deleted = repo.delete_note(note.filename)

    assert deleted is True
    assert not (tmp_path / "notes" / note.filename).exists()


def test_delete_note_returns_false_for_missing_file(tmp_path):
    repo = NoteRepository(notes_home=tmp_path)

    deleted = repo.delete_note("missing-note.md")

    assert deleted is False


def test_save_and_load_preserves_archived_metadata(tmp_path):
    repo = NoteRepository(notes_home=tmp_path)
    note = make_sample_note(
        filename="archived.md",
        title="Archived Note",
        status="archived",
        archived_at="2026-03-21T12:00:00Z",
    )

    repo.save_note(note)
    loaded = repo.load_note("archived.md")

    assert loaded is not None
    assert loaded.status == "archived"
    assert loaded.archived_at == "2026-03-21T12:00:00Z"


def test_save_note_writes_expected_yaml_fields(tmp_path):
    repo = NoteRepository(notes_home=tmp_path)
    note = make_sample_note(
        filename="yaml-check.md",
        title="YAML Check",
        tags=["python", "testing"],
        status="archived",
        priority=2,
        archived_at="2026-03-21T09:30:00Z",
    )

    repo.save_note(note)

    saved_file = tmp_path / "notes" / "yaml-check.md"
    text = saved_file.read_text(encoding="utf-8")

    assert "title: YAML Check" in text
    assert "author: James" in text
    assert "created: 2026-03-20T10:00:00Z" in text
    assert "modified: 2026-03-20T10:00:00Z" in text
    assert "tags: [python, testing]" in text
    assert "status: archived" in text
    assert "priority: 2" in text
    assert "archived_at: 2026-03-21T09:30:00Z" in text
    assert "This is a test note." in text