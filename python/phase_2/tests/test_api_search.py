def seed_note(api_client, filename, title, content, tags=None):
    return api_client.post(
        "/api/notes",
        json={
            "filename": filename,
            "title": title,
            "author": "James",
            "content": content,
            "tags": tags or [],
        },
    )


def seed_dataset(api_client, filename, title, raw_content, tags=None, schema=None):
    return api_client.post(
        "/api/datasets",
        json={
            "filename": filename,
            "raw_content": raw_content,
            "title": title,
            "author": "James",
            "tags": tags or [],
            "schema": schema or [],
            "row_count": 1,
            "profile": None,
        },
    )


def test_search_all_returns_note_and_dataset_results(api_client):
    seed_note(api_client, "python.md", "Python Note", "Learning Python", ["code"])
    seed_dataset(
        api_client,
        "python.csv",
        "Python Dataset",
        "topic,count\npython,1\n",
        ["data"],
        [{"name": "topic", "type": "string"}],
    )

    response = api_client.get("/api/search?q=python")

    assert response.status_code == 200
    data = response.json()
    types = [item["type"] for item in data]

    assert "note" in types
    assert "dataset" in types


def test_search_notes(api_client):
    seed_note(api_client, "fastapi.md", "FastAPI Note", "FastAPI is great", ["api"])

    response = api_client.get("/api/search/notes?q=fastapi")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "fastapi.md"


def test_search_datasets(api_client):
    seed_dataset(
        api_client,
        "sales.csv",
        "Sales Data",
        "region,amount\nWest,100\n",
        ["sales"],
        [{"name": "region", "type": "string"}],
    )

    response = api_client.get("/api/search/datasets?q=region")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "sales.csv"


def test_search_excludes_archived_notes_by_default(api_client):
    seed_note(api_client, "old.md", "Old Python Note", "Python archive", ["python"])
    api_client.post("/api/notes/old.md/archive")

    response = api_client.get("/api/search/notes?q=python")

    assert response.status_code == 200
    assert response.json() == []


def test_search_can_include_archived_notes(api_client):
    seed_note(api_client, "old.md", "Old Python Note", "Python archive", ["python"])
    api_client.post("/api/notes/old.md/archive")

    response = api_client.get("/api/search/notes?q=python&include_archived=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "old.md"


def test_get_all_tags(api_client):
    seed_note(api_client, "note.md", "Tagged Note", "Content", ["school", "python"])
    seed_dataset(
        api_client,
        "data.csv",
        "Tagged Dataset",
        "x,y\n1,2\n",
        ["data", "python"],
        [],
    )

    response = api_client.get("/api/tags")

    assert response.status_code == 200
    tags = response.json()["tags"]

    assert "school" in tags
    assert "python" in tags
    assert "data" in tags


def test_get_note_tags(api_client):
    seed_note(api_client, "note.md", "Tagged Note", "Content", ["school", "python"])

    response = api_client.get("/api/tags/notes")

    assert response.status_code == 200
    tags = response.json()["tags"]

    assert "school" in tags
    assert "python" in tags


def test_get_dataset_tags(api_client):
    seed_dataset(
        api_client,
        "data.csv",
        "Tagged Dataset",
        "x,y\n1,2\n",
        ["data", "python"],
        [],
    )

    response = api_client.get("/api/tags/datasets")

    assert response.status_code == 200
    tags = response.json()["tags"]

    assert "data" in tags
    assert "python" in tags


def test_search_all_by_tag(api_client):
    seed_note(api_client, "note.md", "School Note", "Content", ["school"])
    seed_dataset(
        api_client,
        "data.csv",
        "School Dataset",
        "x,y\n1,2\n",
        ["school"],
        [],
    )

    response = api_client.get("/api/search/tag/school")

    assert response.status_code == 200
    data = response.json()
    types = [item["type"] for item in data]

    assert "note" in types
    assert "dataset" in types


def test_filter_notes_by_date_route(api_client):
    seed_note(api_client, "dated.md", "Dated", "Content", ["dated"])
    note = api_client.get("/api/notes/dated.md").json()
    created = note["created"]

    response = api_client.get(
        f"/api/notes/filter/by-date?start_date={created}&date_field=created&include_archived=true"
    )

    assert response.status_code == 200
    data = response.json()
    filenames = [item["filename"] for item in data]
    assert "dated.md" in filenames


def test_blank_search_returns_422_for_required_query_param(api_client):
    response = api_client.get("/api/search")

    assert response.status_code == 422