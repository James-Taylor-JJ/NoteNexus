import pytest


def test_list_datasets_returns_saved_datasets(dataset_service):
    dataset_service.create_dataset(
        filename="sales.csv",
        raw_content="id,amount\n1,100\n2,250\n",
        title="Sales",
        author="James",
    )

    datasets = dataset_service.list_datasets()

    assert len(datasets) == 1
    assert datasets[0].filename == "sales.csv"
    assert datasets[0].title == "Sales"


def test_read_dataset_returns_dataset_when_present(dataset_service):
    dataset_service.create_dataset(
        filename="sales.csv",
        raw_content="id,amount\n1,100\n",
        title="Sales",
        author="James",
    )

    dataset = dataset_service.read_dataset("sales.csv")

    assert dataset is not None
    assert dataset.filename == "sales.csv"
    assert dataset.title == "Sales"


def test_read_dataset_returns_none_when_missing(dataset_service):
    dataset = dataset_service.read_dataset("missing.csv")

    assert dataset is None


def test_create_dataset_rejects_empty_filename(dataset_service):
    with pytest.raises(ValueError, match="filename is required"):
        dataset_service.create_dataset(
            filename="",
            raw_content="id,amount\n1,100\n",
            title="Sales",
            author="James",
        )


def test_create_dataset_rejects_invalid_extension(dataset_service):
    with pytest.raises(ValueError, match="Unsupported dataset format"):
        dataset_service.create_dataset(
            filename="sales.xlsx",
            raw_content="fake data",
            title="Sales",
            author="James",
        )


def test_create_dataset_rejects_duplicate_filename(dataset_service):
    dataset_service.create_dataset(
        filename="sales.csv",
        raw_content="id,amount\n1,100\n",
        title="Sales",
        author="James",
    )

    with pytest.raises(ValueError, match="already exists"):
        dataset_service.create_dataset(
            filename="sales.csv",
            raw_content="id,amount\n2,200\n",
            title="Sales 2",
            author="James",
        )


def test_create_dataset_sets_defaults(dataset_service):
    dataset = dataset_service.create_dataset(
        filename="inventory.csv",
        raw_content="id,name\n1,Widget\n",
        title="",
        author="",
    )

    assert dataset.filename == "inventory.csv"
    assert dataset.title == "inventory"
    assert dataset.author == "Unknown"
    assert dataset.format == "csv"
    assert dataset.path == "inventory.csv"


def test_preview_dataset_returns_limited_rows(dataset_service):
    dataset_service.create_dataset(
        filename="sales.csv",
        raw_content="id,amount\n1,100\n2,250\n3,300\n",
        title="Sales",
        author="James",
    )

    preview = dataset_service.preview_dataset("sales.csv", limit=2)

    assert len(preview) == 2
    assert preview[0]["id"] == "1"
    assert preview[1]["id"] == "2"


def test_preview_dataset_rejects_invalid_limit(dataset_service):
    dataset_service.create_dataset(
        filename="sales.csv",
        raw_content="id,amount\n1,100\n",
        title="Sales",
        author="James",
    )

    with pytest.raises(ValueError, match="at least 1"):
        dataset_service.preview_dataset("sales.csv", limit=0)


def test_delete_dataset_removes_existing_dataset(dataset_service, dataset_repo):
    dataset_service.create_dataset(
        filename="sales.csv",
        raw_content="id,amount\n1,100\n",
        title="Sales",
        author="James",
    )

    deleted = dataset_service.delete_dataset("sales.csv")

    assert deleted is True
    assert dataset_repo.load_dataset("sales.csv") is None


def test_delete_dataset_returns_false_when_missing(dataset_service):
    deleted = dataset_service.delete_dataset("missing.csv")

    assert deleted is False


def test_update_dataset_metadata_updates_fields(dataset_service):
    dataset_service.create_dataset(
        filename="sales.csv",
        raw_content="id,amount\n1,100\n",
        title="Sales",
        author="James",
        tags=["finance"],
        schema=[{"name": "id", "type": "integer"}],
        row_count=1,
    )

    updated = dataset_service.update_dataset_metadata(
        filename="sales.csv",
        title="Updated Sales",
        author="Taylor",
        tags=["finance", "quarterly"],
        schema=[{"name": "amount", "type": "number"}],
        row_count=10,
        profile={"quality": "good"},
    )

    assert updated is not None
    assert updated.title == "Updated Sales"
    assert updated.author == "Taylor"
    assert updated.tags == ["finance", "quarterly"]
    assert updated.schema == [{"name": "amount", "type": "number"}]
    assert updated.row_count == 10
    assert updated.profile == {"quality": "good"}


def test_update_dataset_metadata_returns_none_when_missing(dataset_service):
    updated = dataset_service.update_dataset_metadata(
        filename="missing.csv",
        title="Nope",
    )

    assert updated is None