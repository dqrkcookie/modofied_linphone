"""
Example test file for Linphone Caller API.

Run with: pytest tests/
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "linphone_available" in data
    assert "timestamp" in data


def test_list_calls_empty():
    """Test listing calls when none are active."""
    response = client.get("/api/v1/calls")
    assert response.status_code == 200
    data = response.json()
    assert "active_calls" in data
    assert "total" in data
    assert isinstance(data["active_calls"], list)


def test_get_nonexistent_call():
    """Test getting status of non-existent call."""
    response = client.get("/api/v1/call/nonexistent/status")
    assert response.status_code == 404


def test_start_call_invalid_destination():
    """Test starting call with invalid destination."""
    response = client.post("/api/v1/call/start", json={
        "destination": "invalid-uri"
    })
    assert response.status_code == 422  # Validation error


def test_inject_audio_invalid_call():
    """Test injecting audio into non-existent call."""
    response = client.post("/api/v1/call/nonexistent/inject-audio", json={
        "audio_file_name": "test.wav"
    })
    assert response.status_code == 404


def test_inject_audio_invalid_file():
    """Test injecting audio with invalid file format."""
    response = client.post("/api/v1/call/test/inject-audio", json={
        "audio_file_name": "test.mp3"
    })
    assert response.status_code == 422  # Validation error


def test_inject_audio_path_traversal():
    """Test audio injection with path traversal attempt."""
    response = client.post("/api/v1/call/test/inject-audio", json={
        "audio_file_name": "../../../etc/passwd.wav"
    })
    assert response.status_code == 422  # Validation error

