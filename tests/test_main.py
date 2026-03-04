import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.llm import RepoSummary
from app.cache import _cache

client = TestClient(app)

def setup_function():
    _cache.clear()

def test_summarize_invalid_url():
    response = client.post("/summarize", json={"github_url": "not-a-url"})
    assert response.status_code == 422
    assert response.json() == {"status": "error", "message": "Invalid GitHub URL format"}

@patch("app.main.fetch_repo_data")
@patch("app.main.summarize_with_llm")
def test_summarize_valid_request(mock_summarize, mock_fetch):
    mock_fetch.return_value = {"tree": "tree", "files": {"file.txt": "content"}}
    mock_summarize.return_value = RepoSummary(
        summary="A test repo",
        technologies=["Python"],
        structure="One file"
    )

    response = client.post("/summarize", json={"github_url": "https://github.com/a/b"})

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "technologies" in data
    assert "structure" in data
    assert data["summary"] == "A test repo"

@patch("app.main.fetch_repo_data")
def test_summarize_repo_not_found(mock_fetch):
    mock_fetch.side_effect = ValueError("not_found")
    response = client.post("/summarize", json={"github_url": "https://github.com/a/b"})
    assert response.status_code == 404

@patch("app.main.fetch_repo_data")
def test_summarize_rate_limited(mock_fetch):
    mock_fetch.side_effect = ValueError("rate_limited")
    response = client.post("/summarize", json={"github_url": "https://github.com/a/b"})
    assert response.status_code == 429

@patch("app.main.fetch_repo_data")
def test_summarize_github_error(mock_fetch):
    mock_fetch.side_effect = Exception("Some generic error")
    response = client.post("/summarize", json={"github_url": "https://github.com/a/b"})
    assert response.status_code == 502

@patch("app.main.fetch_repo_data")
@patch("app.main.summarize_with_llm")
def test_summarize_llm_error(mock_summarize, mock_fetch):
    mock_fetch.return_value = {"tree": "tree", "files": {}}
    mock_summarize.side_effect = Exception("LLM generic error")
    response = client.post("/summarize", json={"github_url": "https://github.com/a/b"})
    assert response.status_code == 502

@patch("app.main.fetch_repo_data")
@patch("app.main.summarize_with_llm")
def test_summarize_cache_hit(mock_summarize, mock_fetch):
    mock_fetch.return_value = {"tree": "tree", "files": {"file.txt": "content"}}
    mock_summarize.return_value = RepoSummary(
        summary="A test repo",
        technologies=["Python"],
        structure="One file"
    )

    # First call
    response1 = client.post("/summarize", json={"github_url": "https://github.com/a/b"})
    assert response1.headers.get("X-Cache") == "MISS"

    # Second call
    response2 = client.post("/summarize", json={"github_url": "https://github.com/a/b"})
    assert response2.headers.get("X-Cache") == "HIT"

    # Fetch and summarize should only be called once
    mock_fetch.assert_called_once()
    mock_summarize.assert_called_once()

@patch("app.main.fetch_repo_data")
@patch("app.main.summarize_with_llm")
def test_summarize_returns_x_cache_miss_header(mock_summarize, mock_fetch):
    mock_fetch.return_value = {"tree": "tree", "files": {}}
    mock_summarize.return_value = RepoSummary(summary="sum", technologies=[], structure="struct")
    response = client.post("/summarize", json={"github_url": "https://github.com/a/b"})
    assert response.headers.get("X-Cache") == "MISS"
