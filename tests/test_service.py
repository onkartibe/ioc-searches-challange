import pytest
from app.models import SubmitRequest, DataEntry
from app.service import DataService
from app.repository import InMemoryRepository

@pytest.fixture
def service():
    repo = InMemoryRepository()
    return DataService(repo)

def test_submit_valid_ip(service):
    req = SubmitRequest(value="1.2.3.4", tags=["malware"])
    entry_id = service.submit(req)
    assert isinstance(entry_id, str)

def test_submit_valid_domain(service):
    req = SubmitRequest(value="example.com", tags=["phishing"])
    entry_id = service.submit(req)
    assert isinstance(entry_id, str)

def test_submit_valid_hash(service):
    req = SubmitRequest(
        value="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        tags=[]
    )
    entry_id = service.submit(req)
    assert isinstance(entry_id, str)

def test_submit_invalid_value(service):
    req = SubmitRequest(value="notavalidtype", tags=["foo"])
    with pytest.raises(ValueError, match="Value must be a valid IP, domain, or hash."):
        service.submit(req)

def test_submit_empty_value(service):
    req = SubmitRequest(value="", tags=["foo"])
    with pytest.raises(ValueError, match="Value must not be empty."):
        service.submit(req)

def test_submit_invalid_tags(service):
    req = SubmitRequest(value="1.2.3.4", tags=["", "  "])
    with pytest.raises(ValueError, match="All tags must be non-empty strings."):
        service.submit(req)

def test_submit_duplicate(service):
    req1 = SubmitRequest(value="5.6.7.8", tags=["A", "B"])
    req2 = SubmitRequest(value="5.6.7.8", tags=["b", "a"])
    service.submit(req1)
    with pytest.raises(ValueError, match="Duplicate entry"):
        service.submit(req2)

def test_search_basic(service):
    req = SubmitRequest(value="8.8.8.8", tags=["dns"])
    service.submit(req)
    results = service.search("8.8.8.8", ["dns"], 10)
    assert any(e.value == "8.8.8.8" for e in results)

def test_search_tag_case_insensitive(service):
    req = SubmitRequest(value="abc.com", tags=["foo", "bar"])
    service.submit(req)
    results = service.search("abc.com", ["FOO", "BAR"], 10)
    assert any(e.value == "abc.com" for e in results)

def test_search_limit(service):
    for i in range(5):
        req = SubmitRequest(value="limittest.com", tags=[f"t{i}"])
        service.submit(req)
    results = service.search("limittest.com", [], 3)
    assert len(results) == 3
