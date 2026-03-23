import csv
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

import yaml

from python.phase_2.models.dataset_asset import DatasetAsset


class DatasetRepository:
    def __init__(self, notes_home: Optional[Path] = None):
        self.notes_home = notes_home or (Path.home() / ".notes")
        self.datasets_dir = self.notes_home / "datasets"

    def ensure_datasets_dir(self) -> Path:
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        return self.datasets_dir

    def get_dataset_files(self) -> List[Path]:
        self.ensure_datasets_dir()
        dataset_files = []
        dataset_files.extend(self.datasets_dir.glob("*.csv"))
        dataset_files.extend(self.datasets_dir.glob("*.json"))
        return sorted(dataset_files)

    def sidecar_path_for(self, data_file: Path) -> Path:
        return data_file.with_suffix(data_file.suffix + ".dataset.yml")

    def write_sidecar_metadata(self, file_path: Path, metadata: Dict[str, Any]) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(metadata, f, sort_keys=False, allow_unicode=True)

    def read_sidecar_metadata(self, file_path: Path) -> Dict[str, Any]:
        if not file_path.exists():
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def save_dataset_file(self, filename: str, content: str) -> Path:
        self.ensure_datasets_dir()
        file_path = self.datasets_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def save_dataset(self, dataset: DatasetAsset, raw_content: str) -> None:
        file_path = self.save_dataset_file(dataset.filename, raw_content)
        sidecar_path = self.sidecar_path_for(file_path)

        metadata = {
            "id": dataset.asset_id,
            "title": dataset.title,
            "author": dataset.author,
            "created": dataset.created,
            "modified": dataset.modified,
            "tags": dataset.tags,
            "format": dataset.format,
            "path": dataset.path,
            "rowCount": dataset.row_count,
            "schema": dataset.schema,
        }

        if dataset.profile is not None:
            metadata["profile"] = dataset.profile

        self.write_sidecar_metadata(sidecar_path, metadata)

    def load_dataset(self, filename: str) -> Optional[DatasetAsset]:
        file_path = self.datasets_dir / filename
        if not file_path.exists():
            return None

        metadata = self.read_sidecar_metadata(self.sidecar_path_for(file_path))

        return DatasetAsset(
            asset_id=metadata.get("id", ""),
            asset_type="dataset",
            title=metadata.get("title", file_path.stem),
            author=metadata.get("author", "Unknown"),
            created=metadata.get("created", ""),
            modified=metadata.get("modified", ""),
            tags=metadata.get("tags", []) or [],
            filename=file_path.name,
            format=metadata.get("format", file_path.suffix.lstrip(".")),
            path=metadata.get("path", file_path.name),
            row_count=metadata.get("rowCount", 0),
            schema=metadata.get("schema", []) or [],
            profile=metadata.get("profile"),
        )

    def load_all_datasets(self) -> List[DatasetAsset]:
        datasets = []
        for path in self.get_dataset_files():
            dataset = self.load_dataset(path.name)
            if dataset:
                datasets.append(dataset)
        return datasets

    def delete_dataset(self, filename: str) -> bool:
        file_path = self.datasets_dir / filename
        if not file_path.exists():
            return False

        sidecar_path = self.sidecar_path_for(file_path)
        file_path.unlink()

        if sidecar_path.exists():
            sidecar_path.unlink()

        return True

    def preview_dataset(self, filename: str, limit: int = 5) -> List[Dict[str, Any]]:
        file_path = self.datasets_dir / filename
        if not file_path.exists():
            return []

        # CSV preview
        if file_path.suffix == ".csv":
            with open(file_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                rows = []
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    rows.append(row)
                return rows

        # JSON preview
        elif file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, list):
                    return data[:limit]

                if isinstance(data, dict):
                    return [data]

        return []