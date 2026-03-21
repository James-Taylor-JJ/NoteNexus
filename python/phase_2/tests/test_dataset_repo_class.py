import json

from phase_2.models.dataset_asset import DatasetAsset
from phase_2.repositories.dataset_repo_class import DatasetRepository


def make_sample_dataset(
    filename="sales.csv",
    title="Sales Data",
    author="James",
    created="2026-03-20T10:00:00Z",
    modified="2026-03-20T10:00:00Z",
    tags=None,
    row_count=3,
    schema=None,
    profile=None,
):
    return DatasetAsset(
        asset_id=filename,
        asset_type="dataset",
        title=title,
        author=author,
        created=created,
        modified=modified,
        tags=tags or ["sales", "finance"],
        filename=filename,
        format=filename.split(".")[-1],
        path=filename,
        row_count=row_count,
        schema=schema or [
            {"name": "id", "type": "integer"},
            {"name": "amount", "type": "number"},
        ],
        profile=profile,
    )


def test_ensure_datasets_dir_creates_directory(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)

    datasets_dir = repo.ensure_datasets_dir()

    assert datasets_dir.exists()
    assert datasets_dir.is_dir()
    assert datasets_dir == tmp_path / "datasets"


def test_save_dataset_creates_raw_file_and_sidecar(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)
    dataset = make_sample_dataset()
    raw_content = "id,amount\n1,100\n2,250\n3,300\n"

    repo.save_dataset(dataset, raw_content)

    raw_file = tmp_path / "datasets" / "sales.csv"
    sidecar = tmp_path / "datasets" / "sales.csv.dataset.yml"

    assert raw_file.exists()
    assert sidecar.exists()


def test_load_dataset_returns_saved_dataset(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)
    dataset = make_sample_dataset()
    raw_content = "id,amount\n1,100\n2,250\n3,300\n"

    repo.save_dataset(dataset, raw_content)
    loaded = repo.load_dataset("sales.csv")

    assert loaded is not None
    assert loaded.filename == dataset.filename
    assert loaded.title == dataset.title
    assert loaded.author == dataset.author
    assert loaded.created == dataset.created
    assert loaded.modified == dataset.modified
    assert loaded.tags == dataset.tags
    assert loaded.row_count == dataset.row_count
    assert loaded.schema == dataset.schema


def test_load_dataset_returns_none_when_missing(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)

    loaded = repo.load_dataset("missing.csv")

    assert loaded is None


def test_load_all_datasets_returns_all_saved_datasets(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)

    dataset1 = make_sample_dataset(filename="a.csv", title="A")
    dataset2 = make_sample_dataset(filename="b.json", title="B")
    repo.save_dataset(dataset1, "id,amount\n1,100\n")
    repo.save_dataset(dataset2, '[{"id": 1, "amount": 200}]')

    datasets = repo.load_all_datasets()
    filenames = [dataset.filename for dataset in datasets]

    assert len(datasets) == 2
    assert "a.csv" in filenames
    assert "b.json" in filenames


def test_delete_dataset_removes_raw_file_and_sidecar(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)
    dataset = make_sample_dataset()
    repo.save_dataset(dataset, "id,amount\n1,100\n")

    deleted = repo.delete_dataset("sales.csv")

    assert deleted is True
    assert not (tmp_path / "datasets" / "sales.csv").exists()
    assert not (tmp_path / "datasets" / "sales.csv.dataset.yml").exists()


def test_delete_dataset_returns_false_when_missing(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)

    deleted = repo.delete_dataset("missing.csv")

    assert deleted is False


def test_preview_dataset_returns_first_rows_for_csv(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)
    dataset = make_sample_dataset()
    raw_content = "id,amount\n1,100\n2,250\n3,300\n"

    repo.save_dataset(dataset, raw_content)
    preview = repo.preview_dataset("sales.csv", limit=2)

    assert len(preview) == 2
    assert preview[0]["id"] == "1"
    assert preview[0]["amount"] == "100"
    assert preview[1]["id"] == "2"


def test_preview_dataset_returns_first_items_for_json_list(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)
    dataset = make_sample_dataset(filename="people.json", title="People")
    raw_content = json.dumps(
        [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Carol"},
        ]
    )

    repo.save_dataset(dataset, raw_content)
    preview = repo.preview_dataset("people.json", limit=2)

    assert len(preview) == 2
    assert preview[0]["name"] == "Alice"
    assert preview[1]["name"] == "Bob"


def test_preview_dataset_returns_single_item_for_json_object(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)
    dataset = make_sample_dataset(filename="summary.json", title="Summary")
    raw_content = json.dumps({"total": 3, "status": "ok"})

    repo.save_dataset(dataset, raw_content)
    preview = repo.preview_dataset("summary.json", limit=5)

    assert len(preview) == 1
    assert preview[0]["total"] == 3
    assert preview[0]["status"] == "ok"


def test_preview_dataset_returns_empty_list_for_missing_file(tmp_path):
    repo = DatasetRepository(notes_home=tmp_path)

    preview = repo.preview_dataset("missing.csv")

    assert preview == []