from app import crud, schemas


def test_generate_short_code_default_length():
    short_code = crud.generate_short_code()

    assert len(short_code) == 6
    assert short_code.isalnum()


def test_generate_short_code_custom_length():
    short_code = crud.generate_short_code(length=12)

    assert len(short_code) == 12
    assert short_code.isalnum()


def test_create_and_get_short_url(db_session):
    created = crud.create_short_url(
        db_session,
        schemas.URLCreate(original_url="https://example.com/create-crud"),
    )

    found = crud.get_url_by_short_code(db_session, created.short_code)

    assert found is not None
    assert found.id == created.id
    assert found.original_url == "https://example.com/create-crud"
    assert found.access_count == 0


def test_create_duplicate_original_url_gets_distinct_short_codes(db_session):
    first = crud.create_short_url(
        db_session,
        schemas.URLCreate(original_url="https://example.com/duplicate-crud"),
    )
    second = crud.create_short_url(
        db_session,
        schemas.URLCreate(original_url="https://example.com/duplicate-crud"),
    )

    assert first.original_url == second.original_url
    assert first.short_code != second.short_code


def test_update_short_url(db_session):
    created = crud.create_short_url(
        db_session,
        schemas.URLCreate(original_url="https://example.com/before-crud"),
    )

    updated = crud.update_short_url(
        db_session,
        created.short_code,
        schemas.URLUpdate(original_url="https://example.com/after-crud"),
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.original_url == "https://example.com/after-crud"
    assert updated.updated_at >= created.created_at


def test_update_short_url_missing_code_returns_none(db_session):
    updated = crud.update_short_url(
        db_session,
        "missing-code",
        schemas.URLUpdate(original_url="https://example.com/after-crud"),
    )

    assert updated is None


def test_delete_short_url(db_session):
    created = crud.create_short_url(
        db_session,
        schemas.URLCreate(original_url="https://example.com/delete-crud"),
    )

    deleted = crud.delete_short_url(db_session, created.short_code)
    found = crud.get_url_by_short_code(db_session, created.short_code)

    assert deleted is True
    assert found is None


def test_delete_short_url_missing_code_returns_false(db_session):
    deleted = crud.delete_short_url(db_session, "missing-code")

    assert deleted is False


def test_increment_access_count(db_session):
    created = crud.create_short_url(
        db_session,
        schemas.URLCreate(original_url="https://example.com/count-crud"),
    )

    first = crud.increment_access_count(db_session, created)
    second = crud.increment_access_count(db_session, first)

    assert first.access_count == 2
    assert second.access_count == 2


def test_increment_access_count_none_returns_none(db_session):
    assert crud.increment_access_count(db_session, None) is None
