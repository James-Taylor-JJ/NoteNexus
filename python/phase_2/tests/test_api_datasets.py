def test_create_dataset_csv(api_client):
    payload = {
        "filename": "sales.csv",
        "raw_content": "name,amount\nAlice,100\nBob,200\n",
        "title": "Sales Data",
        "author": "James",
        "tags": ["sales", "csv"],
        "schema": [{"name": "name", "type": "string"}, {"name": "amount", "type": "integer"}],
        "row_count": 2,
        "profile": {"sample": True},
    }

    response = api_client.post("/api/datasets", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sales.csv"
    assert data["title"] == "Sales Data"
    assert data["format"] == "csv"
    assert data["row_count"] == 2


def test_create_dataset_rejects_invalid_extension(api_client):
    payload = {
        "filename": "bad.xlsx",
        "raw_content": "not supported",
        "title": "Bad",
        "author": "James",
        "tags": [],
        "schema": [],
        "row_count": 0,
        "profile": None,
    }

    response = api_client.post("/api/datasets", json=payload)

    assert response.status_code == 400
    assert "Unsupported dataset format" in response.json()["detail"]


def test_create_dataset_rejects_duplicate_filename(api_client):
    payload = {
        "filename": "dup.csv",
        "raw_content": "a,b\n1,2\n",
        "title": "Dup",
        "author": "James",
        "tags": [],
        "schema": [],
        "row_count": 1,
        "profile": None,
    }

    first = api_client.post("/api/datasets", json=payload)
    second = api_client.post("/api/datasets", json=payload)

    assert first.status_code == 200
    assert second.status_code == 400
    assert "already exists" in second.json()["detail"]


def test_list_datasets(api_client):
    api_client.post(
        "/api/datasets",
        json={
            "filename": "one.csv",
            "raw_content": "x,y\n1,2\n",
            "title": "One",
            "author": "James",
            "tags": ["one"],
            "schema": [],
            "row_count": 1,
            "profile": None,
        },
    )
    api_client.post(
        "/api/datasets",
        json={
            "filename": "two.json",
            "raw_content": '[{"a":1},{"a":2}]',
            "title": "Two",
            "author": "James",
            "tags": ["two"],
            "schema": [],
            "row_count": 2,
            "profile": None,
        },
    )

    response = api_client.get("/api/datasets")

    assert response.status_code == 200
    filenames = [item["filename"] for item in response.json()]
    assert "one.csv" in filenames
    assert "two.json" in filenames


def test_read_dataset(api_client):
    api_client.post(
        "/api/datasets",
        json={
            "filename": "people.json",
            "raw_content": '[{"name":"Alice"}]',
            "title": "People",
            "author": "James",
            "tags": ["people"],
            "schema": [{"name": "name", "type": "string"}],
            "row_count": 1,
            "profile": None,
        },
    )

    response = api_client.get("/api/datasets/people.json")

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "people.json"
    assert data["title"] == "People"
    assert data["format"] == "json"


def test_read_dataset_returns_404_when_missing(api_client):
    response = api_client.get("/api/datasets/missing.csv")

    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset not found"


def test_preview_csv_dataset(api_client):
    api_client.post(
        "/api/datasets",
        json={
            "filename": "preview.csv",
            "raw_content": "name,amount\nAlice,100\nBob,200\nCarol,300\n",
            "title": "Preview CSV",
            "author": "James",
            "tags": [],
            "schema": [],
            "row_count": 3,
            "profile": None,
        },
    )

    response = api_client.get("/api/datasets/preview.csv/preview?limit=2")

    assert response.status_code == 200
    preview = response.json()["preview"]
    assert len(preview) == 2
    assert preview[0]["name"] == "Alice"
    assert preview[1]["name"] == "Bob"


def test_preview_json_dataset(api_client):
    api_client.post(
        "/api/datasets",
        json={
            "filename": "preview.json",
            "raw_content": '[{"name":"Alice"},{"name":"Bob"},{"name":"Carol"}]',
            "title": "Preview JSON",
            "author": "James",
            "tags": [],
            "schema": [],
            "row_count": 3,
            "profile": None,
        },
    )

    response = api_client.get("/api/datasets/preview.json/preview?limit=2")

    assert response.status_code == 200
    preview = response.json()["preview"]
    assert len(preview) == 2
    assert preview[0]["name"] == "Alice"
    assert preview[1]["name"] == "Bob"


def test_update_dataset_metadata(api_client):
    api_client.post(
        "/api/datasets",
        json={
            "filename": "update.csv",
            "raw_content": "name,amount\nAlice,100\n",
            "title": "Old Title",
            "author": "James",
            "tags": ["old"],
            "schema": [],
            "row_count": 1,
            "profile": None,
        },
    )

    response = api_client.patch(
        "/api/datasets/update.csv/metadata",
        json={
            "title": "New Title",
            "tags": ["new", "sales"],
            "row_count": 99,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["tags"] == ["new", "sales"]
    assert data["row_count"] == 99


def test_update_dataset_metadata_returns_404_when_missing(api_client):
    response = api_client.patch(
        "/api/datasets/missing.csv/metadata",
        json={"title": "Nothing"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset not found"


def test_delete_dataset(api_client):
    api_client.post(
        "/api/datasets",
        json={
            "filename": "delete.csv",
            "raw_content": "a,b\n1,2\n",
            "title": "Delete Dataset",
            "author": "James",
            "tags": [],
            "schema": [],
            "row_count": 1,
            "profile": None,
        },
    )

    response = api_client.delete("/api/datasets/delete.csv")

    assert response.status_code == 200
    assert response.json()["message"] == "delete.csv deleted"

    after = api_client.get("/api/datasets/delete.csv")
    assert after.status_code == 404


def test_delete_dataset_returns_404_when_missing(api_client):
    response = api_client.delete("/api/datasets/missing.csv")

    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset not found"