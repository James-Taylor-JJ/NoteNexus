from fastapi import APIRouter, Depends, HTTPException, Query, status

from phase_2.api.deps import get_dataset_service
from phase_2.api.schemas import (
    DatasetCreateRequest,
    DatasetMetadataUpdateRequest,
    DatasetResponse,
    DeleteResponse,
)
from phase_2.services.dataset_service_class import DatasetService

router = APIRouter(prefix="/datasets", tags=["datasets"])


def to_dataset_response(dataset) -> DatasetResponse:
    return DatasetResponse(
        asset_id=dataset.asset_id,
        asset_type=dataset.asset_type,
        title=dataset.title,
        author=dataset.author,
        created=dataset.created,
        modified=dataset.modified,
        tags=dataset.tags,
        filename=dataset.filename,
        format=dataset.format,
        path=dataset.path,
        row_count=dataset.row_count,
        schema=dataset.schema,
        profile=dataset.profile,
    )


@router.get("", response_model=list[DatasetResponse])
def list_datasets(service: DatasetService = Depends(get_dataset_service)):
    datasets = service.list_datasets()
    return [to_dataset_response(ds) for ds in datasets]


@router.get("/{filename}", response_model=DatasetResponse)
def read_dataset(filename: str, service: DatasetService = Depends(get_dataset_service)):
    dataset = service.read_dataset(filename)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return to_dataset_response(dataset)


@router.get("/{filename}/preview")
def preview_dataset(
    filename: str,
    limit: int = Query(5, ge=1),
    service: DatasetService = Depends(get_dataset_service),
):
    try:
        preview = service.preview_dataset(filename, limit=limit)
        return {"filename": filename, "preview": preview}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(
    payload: DatasetCreateRequest,
    service: DatasetService = Depends(get_dataset_service),
):
    try:
        dataset = service.create_dataset(
            filename=payload.filename,
            raw_content=payload.raw_content,
            title=payload.title,
            author=payload.author,
            tags=payload.tags,
            schema=payload.schema,
            row_count=payload.row_count,
            profile=payload.profile,
        )
        return to_dataset_response(dataset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{filename}/metadata", response_model=DatasetResponse)
def update_dataset_metadata(
    filename: str,
    payload: DatasetMetadataUpdateRequest,
    service: DatasetService = Depends(get_dataset_service),
):
    dataset = service.update_dataset_metadata(
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
    return to_dataset_response(dataset)


@router.delete("/{filename}", response_model=DeleteResponse)
def delete_dataset(filename: str, service: DatasetService = Depends(get_dataset_service)):
    deleted = service.delete_dataset(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DeleteResponse(deleted=True)