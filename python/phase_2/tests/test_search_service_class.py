def seed_notes(note_service):
    note_service.create_note(
        filename="python-basics.md",
        title="Python Basics",
        author="James",
        content="Learn variables, loops, and functions.",
        tags=["python", "school"],
    )
    note_service.create_note(
        filename="finance-notes.md",
        title="Finance Notes",
        author="Taylor",
        content="Quarterly budget and revenue planning.",
        tags=["finance", "work"],
    )
    note_service.create_note(
        filename="archived-note.md",
        title="Old Archived Note",
        author="James",
        content="This is old content.",
        tags=["archive", "old"],
    )
    note_service.archive_note("archived-note.md")


def seed_datasets(dataset_service):
    dataset_service.create_dataset(
        filename="sales.csv",
        raw_content="id,amount,region\n1,100,East\n2,250,West\n",
        title="Sales Dataset",
        author="James",
        tags=["finance", "quarterly"],
        schema=[
            {"name": "id", "type": "integer"},
            {"name": "amount", "type": "number"},
            {"name": "region", "type": "string"},
        ],
        row_count=2,
    )
    dataset_service.create_dataset(
        filename="students.json",
        raw_content='[{"id": 1, "name": "Alice"}]',
        title="Student Dataset",
        author="Taylor",
        tags=["school", "roster"],
        schema=[
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        row_count=1,
    )


def test_search_notes_finds_matches_in_title_and_content(search_service, note_service):
    seed_notes(note_service)

    results = search_service.search_notes("python")

    assert len(results) == 1
    assert results[0]["type"] == "note"
    assert results[0]["id"] == "python-basics.md"


def test_search_notes_is_case_insensitive(search_service, note_service):
    seed_notes(note_service)

    results = search_service.search_notes("PYTHON")

    assert len(results) == 1
    assert results[0]["id"] == "python-basics.md"


def test_search_notes_excludes_archived_by_default(search_service, note_service):
    seed_notes(note_service)

    results = search_service.search_notes("old")

    assert results == []


def test_search_notes_can_include_archived(search_service, note_service):
    seed_notes(note_service)

    results = search_service.search_notes("old", include_archived=True)

    assert len(results) == 1
    assert results[0]["id"] == "archived-note.md"
    assert results[0]["status"] == "archived"


def test_search_datasets_finds_matches_in_title_and_schema(search_service, dataset_service):
    seed_datasets(dataset_service)

    results = search_service.search_datasets("region")

    assert len(results) == 1
    assert results[0]["type"] == "dataset"
    assert results[0]["id"] == "sales.csv"


def test_search_all_combines_note_and_dataset_results(search_service, note_service, dataset_service):
    seed_notes(note_service)
    seed_datasets(dataset_service)

    results = search_service.search_all("finance")

    ids = [result["id"] for result in results]
    assert "finance-notes.md" in ids
    assert "sales.csv" in ids


def test_get_all_note_tags_returns_unique_sorted_tags(search_service, note_service):
    seed_notes(note_service)

    tags = search_service.get_all_note_tags()

    assert "python" in tags
    assert "school" in tags
    assert "finance" in tags
    assert tags == sorted(tags, key=str.lower)


def test_get_all_dataset_tags_returns_unique_sorted_tags(search_service, dataset_service):
    seed_datasets(dataset_service)

    tags = search_service.get_all_dataset_tags()

    assert "finance" in tags
    assert "quarterly" in tags
    assert "school" in tags
    assert tags == sorted(tags, key=str.lower)


def test_get_all_tags_combines_note_and_dataset_tags(search_service, note_service, dataset_service):
    seed_notes(note_service)
    seed_datasets(dataset_service)

    tags = search_service.get_all_tags()

    assert "python" in tags
    assert "finance" in tags
    assert "school" in tags
    assert "quarterly" in tags


def test_search_notes_by_tag_returns_exact_tag_matches(search_service, note_service):
    seed_notes(note_service)

    results = search_service.search_notes_by_tag("finance")

    assert len(results) == 1
    assert results[0]["id"] == "finance-notes.md"


def test_search_datasets_by_tag_returns_exact_tag_matches(search_service, dataset_service):
    seed_datasets(dataset_service)

    results = search_service.search_datasets_by_tag("school")

    assert len(results) == 1
    assert results[0]["id"] == "students.json"


def test_search_all_by_tag_combines_results(search_service, note_service, dataset_service):
    seed_notes(note_service)
    seed_datasets(dataset_service)

    results = search_service.search_all_by_tag("school")

    ids = [result["id"] for result in results]
    assert "python-basics.md" in ids
    assert "students.json" in ids


def test_filter_notes_by_date_returns_formatted_results(search_service, note_service):
    note_service.create_note(
        filename="recent.md",
        title="Recent",
        author="James",
        content="Recent note",
        tags=["recent"],
    )

    note = note_service.read_note("recent.md")

    results = search_service.filter_notes_by_date(
        start_date=note.created,
        date_field="created",
        include_archived=True,
    )

    assert len(results) >= 1
    assert results[0]["type"] == "note"


def test_search_methods_return_empty_list_for_blank_query(search_service, note_service, dataset_service):
    seed_notes(note_service)
    seed_datasets(dataset_service)

    assert search_service.search_notes("") == []
    assert search_service.search_datasets("   ") == []
    assert search_service.search_all("") == []
    assert search_service.search_notes_by_tag("") == []
    assert search_service.search_datasets_by_tag("   ") == []
    assert search_service.search_all_by_tag("") == []