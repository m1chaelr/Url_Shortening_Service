from datetime import datetime

import pytest

def parse_datetime(value: str):
    return datetime.fromisoformat(value)


def create_short_url(client, original_url: str = "https://example.com/test"):
    response = client.post("/shorten", json={"original_url": original_url})
    assert response.status_code == 201
    return response.json()


def assert_not_found(response):
    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "This is the root endpoint of the server",
    }


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        pytest.param({"original_url": "https://example.com/valid"}, 201, id="valid-url"),
        pytest.param({"original_url": "not-a-url"}, 422, id="invalid-url"),
        pytest.param({}, 422, id="missing-original-url"),
    ],
)
def test_create_short_url_validation(client, payload, expected_status):
    response = client.post("/shorten", json=payload)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "original_url",
    [
        pytest.param("https://example.com/valid", id="valid-fake-url"),
        pytest.param("https://github.com/m1chaelr", id="valid-real-url"),
    ],
)
def test_create_short_url(client, original_url):
    response = client.post("/shorten", json={"original_url": original_url})

    assert response.status_code == 201

    data = response.json()
    assert data["original_url"] == original_url
    assert len(data["short_code"]) == 6
    assert data["access_count"] == 0
    assert isinstance(data["id"], int)
    assert parse_datetime(data["created_at"]) <= parse_datetime(data["updated_at"])


def test_duplicate_original_url_creates_distinct_short_codes(client):
    first = create_short_url(client, "https://example.com/duplicate")
    second = create_short_url(client, "https://example.com/duplicate")

    assert first["original_url"] == second["original_url"]
    assert first["short_code"] != second["short_code"]


@pytest.mark.parametrize(
    "original_url",
    [
        pytest.param("https://example.com/read", id="fake-url"),
        pytest.param("https://github.com/m1chaelr", id="real-url"),
    ],
)
def test_read_short_url_increments_access_count(client, original_url):
    created = create_short_url(client, original_url)

    first_response = client.get(f"/shorten/{created['short_code']}")
    assert first_response.status_code == 200
    first_data = first_response.json()

    assert first_data["original_url"] == original_url
    assert first_data["access_count"] == 1
    assert "id" in first_data
    assert parse_datetime(first_data["created_at"]) <= parse_datetime(first_data["updated_at"])

    second_response = client.get(f"/shorten/{created['short_code']}")
    assert second_response.status_code == 200
    second_data = second_response.json()

    assert second_data["access_count"] == 2
    assert parse_datetime(second_data["created_at"]) == parse_datetime(first_data["created_at"])
    assert parse_datetime(second_data["updated_at"]) > parse_datetime(first_data["updated_at"])


def test_read_short_url_not_found(client):
    response = client.get("/shorten/missing-code")

    assert_not_found(response)


def test_update_short_url(client):
    created = create_short_url(client, "https://example.com/before")

    response = client.put(
        f"/shorten/{created['short_code']}",
        json={"original_url": "https://example.com/after"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == created["short_code"]
    assert data["original_url"] == "https://example.com/after"
    assert parse_datetime(data["created_at"]) == parse_datetime(created["created_at"])
    assert parse_datetime(data["updated_at"]) > parse_datetime(created["updated_at"])


@pytest.mark.parametrize(
    "short_code, payload, expected_status",
    [
        pytest.param("missing-code", {"original_url": "https://example.com/after"}, 404, id="missing-code"),
        pytest.param("missing-code", {"original_url": "not-a-url"}, 422, id="invalid-url"),
    ],
)
def test_update_short_url_error_cases(client, short_code, payload, expected_status):
    response = client.put(f"/shorten/{short_code}", json=payload)

    assert response.status_code == expected_status


def test_delete_short_url(client):
    created = create_short_url(client, "https://example.com/delete")

    delete_response = client.delete(f"/shorten/{created['short_code']}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    read_response = client.get(f"/shorten/{created['short_code']}")
    assert_not_found(read_response)


def test_delete_short_url_not_found(client):
    response = client.delete("/shorten/missing-code")

    assert_not_found(response)


def test_short_url_stats_are_read_only(client):
    created = create_short_url(client, "https://example.com/stats")

    first_response = client.get(f"/shorten/{created['short_code']}/stats")
    assert first_response.status_code == 200
    first_data = first_response.json()

    assert set(first_data.keys()) == {
        "short_code",
        "original_url",
        "created_at",
        "updated_at",
        "access_count",
    }
    assert first_data["short_code"] == created["short_code"]
    assert first_data["original_url"] == "https://example.com/stats"
    assert first_data["access_count"] == 0

    second_response = client.get(f"/shorten/{created['short_code']}/stats")
    assert second_response.status_code == 200
    second_data = second_response.json()

    assert second_data["access_count"] == first_data["access_count"]
    assert parse_datetime(second_data["created_at"]) == parse_datetime(first_data["created_at"])
    assert parse_datetime(second_data["updated_at"]) == parse_datetime(first_data["updated_at"])


def test_short_url_stats_not_found(client):
    response = client.get("/shorten/missing-code/stats")

    assert_not_found(response)


def test_redirect_short_url(client):
    created = create_short_url(client, "https://example.com/redirect-target")

    response = client.get(f"/{created['short_code']}", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/redirect-target"

    stats_response = client.get(f"/shorten/{created['short_code']}/stats")
    assert stats_response.status_code == 200
    assert stats_response.json()["access_count"] == 1


def test_redirect_short_url_not_found(client):
    response = client.get("/missing-code", follow_redirects=False)

    assert_not_found(response)
