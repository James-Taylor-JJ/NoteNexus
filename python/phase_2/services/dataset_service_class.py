from pathlib import Path
from typing import Optional, List, Dict, Any

from python.phase_2.models.dataset_asset import DatasetAsset
from python.phase_2.repositories.dataset_repo_class import DatasetRepository
from python.phase_2.utilities.time_utilities_class import current_timestamp


class DatasetService:
    def __init__(self, repository: DatasetRepository):
        self.repository = repository
        self.allowed_extensions = {".csv", ".json"}

    def _normalize_filename(self, filename: str) -> str:
        filename = filename.strip()
        if not filename:
            raise ValueError("Dataset filename is required.")
        return filename

    def _validate_extension(self, filename: str) -> None:
        suffix = Path(filename).suffix.lower()
        if suffix not in self.allowed_extensions:
            raise ValueError(
                f"Unsupported dataset format: {suffix or '[none]'}. "
                f"Allowed formats are: {', '.join(sorted(self.allowed_extensions))}"
            )

    def _infer_format(self, filename: str) -> str:
        return Path(filename).suffix.lower().lstrip(".")

    def list_datasets(self) -> List[DatasetAsset]:
        return self.repository.load_all_datasets()

    def read_dataset(self, filename: str) -> Optional[DatasetAsset]:
        filename = self._normalize_filename(filename)
        return self.repository.load_dataset(filename)

    def preview_dataset(self, filename: str, limit: int = 5) -> List[Dict[str, Any]]:
        filename = self._normalize_filename(filename)
        if limit < 1:
            raise ValueError("Preview limit must be at least 1.")
        return self.repository.preview_dataset(filename, limit)

    def create_dataset(
        self,
        filename: str,
        raw_content: str,
        title: str = "",
        author: str = "",
        tags: Optional[List[str]] = None,
        schema: Optional[List[Dict[str, Any]]] = None,
        row_count: int = 0,
        profile: Optional[Dict[str, Any]] = None,
    ) -> DatasetAsset:
        filename = self._normalize_filename(filename)
        self._validate_extension(filename)

        existing = self.repository.load_dataset(filename)
        if existing:
            raise ValueError(f"Dataset already exists: {filename}")

        timestamp = current_timestamp()
        dataset = DatasetAsset(
            asset_id=filename,
            asset_type="dataset",
            title=title.strip() or Path(filename).stem,
            author=author.strip() or "Unknown",
            created=timestamp,
            modified=timestamp,
            tags=tags or [],
            filename=filename,
            format=self._infer_format(filename),
            path=filename,
            row_count=row_count,
            schema=schema or [],
            profile=profile,
        )

        self.repository.save_dataset(dataset, raw_content)
        return dataset

    def delete_dataset(self, filename: str) -> bool:
        filename = self._normalize_filename(filename)
        return self.repository.delete_dataset(filename)

    def update_dataset_metadata(
        self,
        filename: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        schema: Optional[List[Dict[str, Any]]] = None,
        row_count: Optional[int] = None,
        profile: Optional[Dict[str, Any]] = None,
    ) -> Optional[DatasetAsset]:
        filename = self._normalize_filename(filename)
        dataset = self.repository.load_dataset(filename)
        if not dataset:
            return None

        raw_path = self.repository.datasets_dir / filename
        if not raw_path.exists():
            return None

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        if title is not None:
            dataset.title = title.strip() or dataset.title
        if author is not None:
            dataset.author = author.strip() or dataset.author
        if tags is not None:
            dataset.tags = tags
        if schema is not None:
            dataset.schema = schema
        if row_count is not None:
            dataset.row_count = row_count
        if profile is not None:
            dataset.profile = profile

        dataset.modified = current_timestamp()

        self.repository.save_dataset(dataset, raw_content)
        return dataset