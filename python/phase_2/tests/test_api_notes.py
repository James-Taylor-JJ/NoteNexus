def test_root_route_returns_running_message(api_client):
    response = api_client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "NoteNexus API is running"}


def test_create_note(api_client):
    payload = {
        "filename": "api-note.md",
        "title": "API Note",
        "author": "James",
        "content": "Created through the API",
        "tags": ["api", "notes"],
    }

    response = api_client.post("/api/notes", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "api-note.md"
    assert data["title"] == "API Note"
    assert data["author"] == "James"
    assert data["content"] == "Created through the API"
    assert data["tags"] == ["api", "notes"]
    assert data["status"] == "active"


def test_create_note_rejects_duplicate_filename(api_client):
    payload = {
        "filename": "duplicate.md",
        "title": "First",
        "author": "James",
        "content": "First content",
        "tags": [],
    }

    first = api_client.post("/api/notes", json=payload)
    second = api_client.post("/api/notes", json=payload)

    assert first.status_code == 200
    assert second.status_code == 400
    assert "already exists" in second.json()["detail"]


def test_list_notes(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "one.md",
            "title": "One",
            "author": "James",
            "content": "First note",
            "tags": ["a"],
        },
    )
    api_client.post(
        "/api/notes",
        json={
            "filename": "two.md",
            "title": "Two",
            "author": "James",
            "content": "Second note",
            "tags": ["b"],
        },
    )

    response = api_client.get("/api/notes")

    assert response.status_code == 200
    data = response.json()
    filenames = [item["filename"] for item in data]

    assert "one.md" in filenames
    assert "two.md" in filenames


def test_read_note(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "readme.md",
            "title": "Read Me",
            "author": "James",
            "content": "Read this note",
            "tags": ["docs"],
        },
    )

    response = api_client.get("/api/notes/readme.md")

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "readme.md"
    assert data["title"] == "Read Me"
    assert data["content"] == "Read this note"


def test_read_note_returns_404_when_missing(api_client):
    response = api_client.get("/api/notes/missing.md")

    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_edit_note(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "editme.md",
            "title": "Edit Me",
            "author": "James",
            "content": "Old content",
            "tags": [],
        },
    )

    response = api_client.put(
        "/api/notes/editme.md",
        json={"content": "New content"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "New content"


def test_edit_note_returns_404_when_missing(api_client):
    response = api_client.put(
        "/api/notes/missing.md",
        json={"content": "Does not matter"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_delete_note(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "deleteme.md",
            "title": "Delete Me",
            "author": "James",
            "content": "Delete this note",
            "tags": [],
        },
    )

    response = api_client.delete("/api/notes/deleteme.md")

    assert response.status_code == 200
    assert response.json()["message"] == "deleteme.md deleted"

    after = api_client.get("/api/notes/deleteme.md")
    assert after.status_code == 404


def test_delete_note_returns_404_when_missing(api_client):
    response = api_client.delete("/api/notes/missing.md")

    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_archive_note(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "archive-me.md",
            "title": "Archive Me",
            "author": "James",
            "content": "Archive this",
            "tags": [],
        },
    )

    response = api_client.post("/api/notes/archive-me.md/archive")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "archived"
    assert data["archived_at"] is not None


def test_restore_note(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "restore-me.md",
            "title": "Restore Me",
            "author": "James",
            "content": "Restore this",
            "tags": [],
        },
    )
    api_client.post("/api/notes/restore-me.md/archive")

    response = api_client.post("/api/notes/restore-me.md/restore")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["archived_at"] is None


def test_archived_notes_are_hidden_by_default(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "active.md",
            "title": "Active",
            "author": "James",
            "content": "Still active",
            "tags": [],
        },
    )
    api_client.post(
        "/api/notes",
        json={
            "filename": "archived.md",
            "title": "Archived",
            "author": "James",
            "content": "Should be hidden",
            "tags": [],
        },
    )
    api_client.post("/api/notes/archived.md/archive")

    response = api_client.get("/api/notes")

    assert response.status_code == 200
    filenames = [item["filename"] for item in response.json()]
    assert "active.md" in filenames
    assert "archived.md" not in filenames


def test_list_notes_can_include_archived(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "archived.md",
            "title": "Archived",
            "author": "James",
            "content": "Include me",
            "tags": [],
        },
    )
    api_client.post("/api/notes/archived.md/archive")

    response = api_client.get("/api/notes?include_archived=true")

    assert response.status_code == 200
    filenames = [item["filename"] for item in response.json()]
    assert "archived.md" in filenames


def test_list_archived_notes(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "archived-only.md",
            "title": "Archived Only",
            "author": "James",
            "content": "Archived note",
            "tags": [],
        },
    )
    api_client.post("/api/notes/archived-only.md/archive")

    response = api_client.get("/api/notes/archived/list")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "archived-only.md"


def test_filter_notes_by_date(api_client):
    api_client.post(
        "/api/notes",
        json={
            "filename": "dated.md",
            "title": "Dated",
            "author": "James",
            "content": "Date filter test",
            "tags": [],
        },
    )

    note = api_client.get("/api/notes/dated.md").json()
    created = note["created"]

    response = api_client.get(
        f"/api/notes/filter/by-date?start_date={created}&date_field=created&include_archived=true"
    )

    assert response.status_code == 200
    filenames = [item["filename"] for item in response.json()]
    assert "dated.md" in filenames


def test_filter_notes_by_date_rejects_invalid_field(api_client):
    response = api_client.get("/api/notes/filter/by-date?date_field=not_real")

    assert response.status_code == 400
    assert "Invalid date field" in response.json()["detail"]