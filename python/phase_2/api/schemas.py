from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NoteCreateRequest(BaseModel):
    filename: str
    title: str
    author: str
    content: str
    tags: List[str] = Field(default_factory=list)


class NoteContentUpdateRequest(BaseModel):
    content: str


class NoteResponse(BaseModel):
    filename: str
    title: str
    content: str
    created: str
    modified: str
    author: str
    tags: List[str]
    status: str
    archived_at: Optional[str] = None


class DatasetCreateRequest(BaseModel):
    filename: str
    raw_content: str
    title: str = ""
    author: str = ""
    tags: List[str] = Field(default_factory=list)
    schema: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    profile: Optional[Dict[str, Any]] = None


class DatasetMetadataUpdateRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    schema: Optional[List[Dict[str, Any]]] = None
    row_count: Optional[int] = None
    profile: Optional[Dict[str, Any]] = None


class DatasetResponse(BaseModel):
    asset_id: str
    asset_type: str
    title: str
    author: str
    created: str
    modified: str
    tags: List[str]
    filename: str
    format: str
    path: str
    row_count: int
    schema: List[Dict[str, Any]]
    profile: Optional[Dict[str, Any]] = None


class SearchResultResponse(BaseModel):
    type: str
    id: str
    title: str
    author: str
    created: str
    modified: str
    tags: List[str]
    status: Optional[str] = None
    archived_at: Optional[str] = None
    format: Optional[str] = None
    row_count: Optional[int] = None


class TagListResponse(BaseModel):
    tags: List[str]


class MessageResponse(BaseModel):
    message: str


class DeleteResponse(BaseModel):
    deleted: bool