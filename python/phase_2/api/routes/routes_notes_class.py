from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from python.phase_2.services.note_service_class import NoteService


class NoteCreateRequest(BaseModel):
    filename: str
    title: str = ""
    author: str = ""
    content: str
    tags: list[str] = Field(default_factory=list)


class NoteEditRequest(BaseModel):
    content: str

def note_to_dict(note) -> dict:
    return {
        "filename": note.filename,
        "title": note.title,
        "author": note.author,
        "content": note.content,
        "created": note.created,
        "modified": note.modified,
        "tags": note.tags,
        "status": note.status,
        "priority": note.priority,
        "archived_at": note.archived_at,
    }


def build_notes_router(note_service: NoteService) -> APIRouter:
    router = APIRouter(prefix="/api/notes", tags=["notes"])

    @router.get("")
    def list_notes(include_archived: bool = False):
        notes = note_service.list_notes(include_archived=include_archived)
        return [note_to_dict(note) for note in notes]

    @router.get("/archived/list")
    def list_archived_notes():
        notes = note_service.list_archived_notes()
        return [note_to_dict(note) for note in notes]

    @router.get("/filter/by-date")
    def filter_notes_by_date(
        start_date: Optional[str] = Query(default=None),
        end_date: Optional[str] = Query(default=None),
        date_field: str = Query(default="modified"),
        include_archived: bool = Query(default=False),
    ):
        try:
            notes = note_service.filter_notes_by_date(
                start_date=start_date,
                end_date=end_date,
                date_field=date_field,
                include_archived=include_archived,
            )
            return [note_to_dict(note) for note in notes]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{filename}")
    def read_note(filename: str):
        note = note_service.read_note(filename)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note_to_dict(note)

    @router.post("")
    def create_note(payload: NoteCreateRequest):
        try:
            note = note_service.create_note(
                filename=payload.filename,
                title=payload.title,
                author=payload.author,
                content=payload.content,
                tags=payload.tags,
            )
            return note_to_dict(note)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.put("/{filename}")
    def edit_note(filename: str, payload: NoteEditRequest):
        note = note_service.edit_note(filename, payload.content)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note_to_dict(note)

    @router.delete("/{filename}")
    def delete_note(filename: str):
        deleted = note_service.delete_note(filename)
        if not deleted:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": f"{filename} deleted"}

    @router.post("/{filename}/archive")
    def archive_note(filename: str):
        note = note_service.archive_note(filename)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note_to_dict(note)

    @router.post("/{filename}/restore")
    def restore_note(filename: str):
        note = note_service.restore_note(filename)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note_to_dict(note)

    return router