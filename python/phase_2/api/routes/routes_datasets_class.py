from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from phase_2.services.dataset_service_class import DatasetService


class DatasetCreateRequest(BaseModel):
    filename: str
    raw_content: str
    title: str = ""
    author: str = ""
    tags: list[str] = Field(default_factory=list)
    schema: list[dict] = Field(default_factory=list)
    row_count: int = 0
    profile: Optional[dict] = None


class DatasetUpdateRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[list[str]] = None
    schema: Optional[list[dict]] = None
    row_count: Optional[int] = None
    profile: Optional[dict] = None


router = APIRouter(prefix="/api/datasets", tags=["datasets"])


def dataset_to_dict(dataset) -> dict:
    return {
        "asset_id": dataset.asset_id,
        "asset_type": dataset.asset_type,
        "filename": dataset.filename,
        "title": dataset.title,
        "author": dataset.author,
        "created": dataset.created,
        "modified": dataset.modified,
        "tags": dataset.tags,
        "format": dataset.format,
        "path": dataset.path,
        "row_count": dataset.row_count,
        "schema": dataset.schema,
        "profile": dataset.profile,
    }


def register_dataset_routes(router: APIRouter, dataset_service: DatasetService) -> None:
    @router.get("")
    def list_datasets():
        datasets = dataset_service.list_datasets()
        return [dataset_to_dict(dataset) for dataset in datasets]

    @router.get("/{filename}")
    def read_dataset(filename: str):
        dataset = dataset_service.read_dataset(filename)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset_to_dict(dataset)

    @router.post("")
    def create_dataset(payload: DatasetCreateRequest):
        try:
            dataset = dataset_service.create_dataset(
                filename=payload.filename,
                raw_content=payload.raw_content,
                title=payload.title,
                author=payload.author,
                tags=payload.tags,
                schema=payload.schema,
                row_count=payload.row_count,
                profile=payload.profile,
            )
            return dataset_to_dict(dataset)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.delete("/{filename}")
    def delete_dataset(filename: str):
        deleted = dataset_service.delete_dataset(filename)
        if not deleted:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return {"message": f"{filename} deleted"}

    @router.get("/{filename}/preview")
    def preview_dataset(filename: str, limit: int = Query(default=5, ge=1)):
        try:
            preview = dataset_service.preview_dataset(filename, limit=limit)
            return {"filename": filename, "preview": preview}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.patch("/{filename}/metadata")
    def update_dataset_metadata(filename: str, payload: DatasetUpdateRequest):
        dataset = dataset_service.update_dataset_metadata(
            filename=filename,
            title=payload.title,
            author=payload.author,
            tags=payload.tags,
            schema=payload.schema,
            row_count=payload.row_count,
            profile=payload.profile,
        )
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset_to_dict(dataset)