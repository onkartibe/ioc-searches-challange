import sys
import os

# Ensure the parent directory is in sys.path so 'main' and 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_submit_valid_ip(client):
    resp = client.post(
        "/submit", json={"value": "1.2.3.4", "tags": ["malware", "test"]}
    )
    assert resp.status_code == 201
    assert "id" in resp.json()


def test_submit_valid_domain(client):
    resp = client.post(
        "/submit", json={"value": "example.com", "tags": ["phishing"]}
    )
    assert resp.status_code == 201
    assert "id" in resp.json()


def test_submit_valid_hash(client):
    resp = client.post(
        "/submit",
        json={
            "value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "tags": [],
        },
    )
    assert resp.status_code == 201
    assert "id" in resp.json()


def test_submit_invalid_value(client):
    resp = client.post(
        "/submit", json={"value": "notavalidtype", "tags": ["foo"]}
    )
    assert resp.status_code == 422
    assert "Value must be a valid IP, domain, or hash." in resp.json()["detail"]


def test_submit_empty_value(client):
    resp = client.post(
        "/submit", json={"value": "", "tags": ["foo"]}
    )
    assert resp.status_code == 422
    assert "Value must not be empty." in resp.json()["detail"]


def test_submit_invalid_tags(client):
    resp = client.post(
        "/submit", json={"value": "1.2.3.4", "tags": ["", "  "]}
    )
    assert resp.status_code == 422
    assert "All tags must be non-empty strings." in resp.json()["detail"]


def test_submit_duplicate(client):
    data = {"value": "5.6.7.8", "tags": ["A", "B"]}
    resp1 = client.post("/submit", json=data)
    assert resp1.status_code == 201
    resp2 = client.post(
        "/submit", json={"value": "5.6.7.8", "tags": ["b", "a"]}
    ) 
    assert resp2.status_code == 409
    assert "Duplicate entry" in resp2.json()["detail"]


def test_get_data_basic(client):
    client.post("/submit", json={"value": "8.8.8.8", "tags": ["dns"]})
    resp = client.get("/data", params={"q": "8.8.8.8"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(e["value"] == "8.8.8.8" for e in data)


def test_get_data_with_tags(client):
    client.post("/submit", json={"value": "abc.com", "tags": ["foo", "bar"]})
    resp = client.get(
        "/data", params={"q": "abc.com", "tags": "foo,bar"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(
        e["value"] == "abc.com" and set(e["tags"]) == {"foo", "bar"} for e in data
    )


def test_get_data_tag_filtering(client):
    client.post("/submit", json={"value": "xyz.com", "tags": ["x", "y"]})
    resp = client.get(
        "/data", params={"q": "xyz.com", "tags": "x"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(e["value"] == "xyz.com" for e in data)
    resp2 = client.get(
        "/data", params={"q": "xyz.com", "tags": "z"}
    )
    assert resp2.status_code == 200
    assert resp2.json()["data"] == []


def test_get_data_limit(client):
    for i in range(5):
        client.post(
            "/submit", json={"value": "limittest.com", "tags": [f"t{i}"]}
        )
    resp = client.get(
        "/data", params={"q": "limittest.com", "limit": 3}
    )
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 3
