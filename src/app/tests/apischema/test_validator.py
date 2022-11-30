from apischema.validator import validate_todo_entry


def test_short_summary_in_todo_entry() -> None:
    data = {
        "summary": "Lo",
        "detail": "",
        "created_at": "2022-09-05T18:07:19.280040+00:00",
        "tag": "new"
    }

    error = validate_todo_entry(raw_data=data)
    assert error.path == "summary"
    assert "maxLength" in error.validation_schema
    assert "minLength" in error.validation_schema
    assert "type" in error.validation_schema


def test_no_tag_in_todo_entry() -> None:
    data = {
        "summary": "Save the world",
        "detail": "",
        "created_at": "2022-09-05T18:07:19.280040+00:00"
    }

    error = validate_todo_entry(raw_data=data)
    assert error is None


def test_no_summary_in_todo_entry() -> None:
    data = {
        "detail": "Some text",
        "created_at": "2022-09-05T18:07:19.280040+00:00",
    }

    error = validate_todo_entry(raw_data=data)
    assert error.message == "'summary' is a required property"


def test_no_created_at_in_todo_entry() -> None:
    data = {
        "summary": "Save the world",
        "detail": "Some text",
    }

    error = validate_todo_entry(raw_data=data)
    assert error.message == "'created_at' is a required property"


def test_no_detail_in_todo_entry() -> None:
    data = {
        "summary": "Save the world",
        "created_at": "2022-09-05T18:07:19.280040+00:00",
        "tag": "not important"
    }

    error = validate_todo_entry(raw_data=data)
    assert error is None
