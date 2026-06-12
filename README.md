# URL Shortening Service

## Overview

This is a Python REST API for shortening URLs, based on the roadmap.sh Backend Roadmap URL Shortening Service project.

The service can create short codes for long URLs, retrieve and update stored URLs, delete short URLs, return usage statistics, and redirect browser requests from a short code to the original URL.

## Tech Stack

- Python 3.12+
- FastAPI
- Uvicorn
- SQLite
- SQLAlchemy
- Pydantic
- pytest

## Features

- Create a shortened URL from a valid original URL.
- Retrieve a stored URL by short code.
- Update the original URL for an existing short code.
- Delete a short URL.
- Return stats for a short URL, including access count.
- Redirect from `/{short_code}` to the original URL.
- Validate request bodies with Pydantic.
- Persist data locally with SQLite.
- Test API and CRUD behavior with pytest.

## Setup

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/shorten` | Create a short URL |
| `GET` | `/shorten/{short_code}` | Retrieve a URL record and increment access count |
| `PUT` | `/shorten/{short_code}` | Update the original URL |
| `DELETE` | `/shorten/{short_code}` | Delete a short URL |
| `GET` | `/shorten/{short_code}/stats` | Return URL stats without incrementing access count |
| `GET` | `/{short_code}` | Redirect to the original URL |

### Create a Short URL

Request:

```bash
curl -X POST http://127.0.0.1:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com"}'
```

Example response:

```json
{
  "id": 1,
  "original_url": "https://example.com",
  "short_code": "abc123",
  "created_at": "2026-06-12T10:00:00.000000",
  "updated_at": "2026-06-12T10:00:00.000000",
  "access_count": 0
}
```

### Retrieve a URL Record

```bash
curl http://127.0.0.1:8000/shorten/abc123
```

This returns the stored URL record and increments `access_count`.

### Update a URL

```bash
curl -X PUT http://127.0.0.1:8000/shorten/abc123 \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.org"}'
```

### Delete a URL

```bash
curl -X DELETE http://127.0.0.1:8000/shorten/abc123
```

Successful deletion returns:

```text
204 No Content
```

### Get URL Stats

```bash
curl http://127.0.0.1:8000/shorten/abc123/stats
```

Example response:

```json
{
  "short_code": "abc123",
  "original_url": "https://example.com",
  "created_at": "2026-06-12T10:00:00.000000",
  "updated_at": "2026-06-12T10:00:00.000000",
  "access_count": 2
}
```

### Redirect

```bash
curl -i http://127.0.0.1:8000/abc123
```

Successful redirects return:

```text
302 Found
Location: https://example.com
```

## Running Tests

Run the test suite:

```bash
pytest -q
```

The tests use a dedicated SQLite database and FastAPI dependency overrides, so they do not depend on the local development database.

## Notes

- Local development data is stored in `url_shortener.db`, which is ignored by Git.
- Tests use `test_url_shortener.db`, which is also ignored by Git.
- Creating the same original URL multiple times currently creates multiple short codes. This is intentional for now.
- Access-count increments are implemented with the ORM object lifecycle for clarity. A production version should consider atomic database updates for high-concurrency traffic.
- The project currently uses SQLite for local development. A production deployment would likely use a database such as PostgreSQL.
