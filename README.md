# FastAPI IOC Submission & Search Service

A FastAPI service for submitting and searching Indicators of Compromise (IOCs) such as IPs, domains, and hashes, with in-memory storage and robust validation.

---

## Project Structure

```
fastapi-template/
├── app/
│   ├── __init__.py
│   ├── api.py           # API route definitions (FastAPI router)
│   ├── models.py        # Pydantic models for request/response/data
│   ├── repository.py    # In-memory repository for storing entries
│   └── service.py       # Business logic and validation
├── main.py              # FastAPI app entrypoint, includes router
├── tests/
│   ├── test_main.py     # Integration tests for API endpoints
│   └── test_service.py  # Unit tests for service logic
├── README.md            # This file
└── venv/                # Python virtual environment
```

- **`app/`**: All application logic, organized for extensibility and maintainability.
- **`main.py`**: Minimal entrypoint, only responsible for app creation and router inclusion.
- **`tests/`**: Contains both integration and unit tests.

---

## Setup

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install runtime dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Install development dependencies (for testing, linting, etc.):**
   ```bash
   pip install -r dev-requirements.txt
   ```

---

## Running the Project

From the project root directory, run:

```bash
uvicorn main:app --reload
```

- The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Running Tests

```bash
pytest
```

- `tests/test_main.py`: Integration tests (API endpoints)
- `tests/test_service.py`: Unit tests (service logic)

---

## Example Requests & Responses

### Submit a new value

**Request**
```http
POST /submit
Content-Type: application/json

{
  "value": "example.org",
  "tags": ["hello", "world"]
}
```

**Response**
```json
{
  "id": "c2b2f7e2-2e2e-4e2e-8e2e-2e2e2e2e2e2e"
}
```

---

### Search for a value

**Request**
```http
GET /data?q=example.org&tags=hello,world&limit=5
```

**Response**
```json
{
  "data": [
    {
      "value": "example.org",
      "tags": ["hello", "world"],
      "type": "domain"
    }
  ]
}
```

---

### Duplicate Submission

**Request**
```http
POST /submit
Content-Type: application/json

{
  "value": "example.org",
  "tags": ["hello", "world"]
}
```

**Response**
```json
{
  "detail": "Duplicate entry: value with same tags and type already exists."
}
```

---

### Invalid Value

**Request**
```http
POST /submit
Content-Type: application/json

{
  "value": "notavalidtype",
  "tags": ["foo"]
}
```

**Response**
```json
{
  "detail": "Value must be a valid IP, domain, or hash."
}
```

---

## Design Notes

- **Clean Architecture**:  
  The code is modular, separating models, repository, service, and API layers for clarity and extensibility.

- **Dependency Injection**:  
  FastAPI's `Depends` is used for injecting the service layer, making the code testable and flexible.

- **In-Memory Storage**:  
  All data is stored in-memory for simplicity and speed. The repository can be swapped for a persistent backend with minimal changes.

- **De-duplication**:  
  Submissions with the same value, tags (case-insensitive, order-insensitive), and type are rejected with a helpful error.

- **Validation**:  
  Input is validated with clear error messages for empty values, invalid types, or duplicate entries. Tags must be non-empty strings.

- **Case-insensitive Tag Filtering**:  
  Tag matching during search is case-insensitive.

- **Extensible Structure**:  
  The project is structured for easy extension (e.g., adding authentication, persistent storage, or new endpoints).

- **Testable**:  
  The service and repository are easily testable; see `tests/test_main.py` and `tests/test_service.py` for examples.

---

## Extending the Project

- To add persistent storage, implement a new repository class and swap it in `app/api.py`.
- To add authentication, use FastAPI dependencies in `app/api.py`.
- To add new endpoints, define them in `app/api.py` and update the router.

---

## Troubleshooting

- Ensure you run all commands from the project root so that the `app` package is discoverable.
- If you encounter import errors, check that `app/__init__.py` exists and all imports use the `app.` prefix.

---
