from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.deps import get_note_service
from api.schemas import (
    DeleteResponse,
    MessageResponse,
    NoteContentUpdateRequest,
    NoteCreateRequest,
    NoteResponse,
)
from services.note_service_class import NoteService

router = APIRouter(prefix="/notes", tags=["notes"])


def to_note_response(note) -> NoteResponse:
    return NoteResponse(
        filename=note.filename,
        title=note.title,
        content=note.content,
        created=note.created,
        modified=note.modified,
        author=note.author,
        tags=note.tags,
        status=note.status,
        archived_at=note.archived_at,
    )


@router.get("", response_model=list[NoteResponse])
def list_notes(
    include_archived: bool = Query(False),
    service: NoteService = Depends(get_note_service),
):
    notes = service.list_notes(include_archived=include_archived)
    return [to_note_response(note) for note in notes]


@router.get("/archived", response_model=list[NoteResponse])
def list_archived_notes(service: NoteService = Depends(get_note_service)):
    notes = service.list_archived_notes()
    return [to_note_response(note) for note in notes]


@router.get("/filter/by-date", response_model=list[NoteResponse])
def filter_notes_by_date(
    start_date: str | None = None,
    end_date: str | None = None,
    date_field: str = "modified",
    include_archived: bool = False,
    service: NoteService = Depends(get_note_service),
):
    try:
        notes = service.filter_notes_by_date(
            start_date=start_date,
            end_date=end_date,
            date_field=date_field,
            include_archived=include_archived,
        )
        return [to_note_response(note) for note in notes]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{filename}", response_model=NoteResponse)
def read_note(filename: str, service: NoteService = Depends(get_note_service)):
    note = service.read_note(filename)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return to_note_response(note)


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreateRequest, service: NoteService = Depends(get_note_service)):
    try:
        note = service.create_note(
            filename=payload.filename,
            title=payload.title,
            author=payload.author,
            content=payload.content,
            tags=payload.tags,
        )
        return to_note_response(note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{filename}/content", response_model=NoteResponse)
def edit_note_content(
    filename: str,
    payload: NoteContentUpdateRequest,
    service: NoteService = Depends(get_note_service),
):
    note = service.edit_note(filename, payload.content)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return to_note_response(note)


@router.post("/{filename}/archive", response_model=NoteResponse)
def archive_note(filename: str, service: NoteService = Depends(get_note_service)):
    note = service.archive_note(filename)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return to_note_response(note)


@router.post("/{filename}/restore", response_model=NoteResponse)
def restore_note(filename: str, service: NoteService = Depends(get_note_service)):
    note = service.restore_note(filename)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return to_note_response(note)


@router.delete("/{filename}", response_model=DeleteResponse)
def delete_note(filename: str, service: NoteService = Depends(get_note_service)):
    deleted = service.delete_note(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return DeleteResponse(deleted=True)