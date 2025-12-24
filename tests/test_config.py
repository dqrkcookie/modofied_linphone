"""
Test configuration and models.
"""
import pytest
from app.core.config import get_settings, get_project_root
from app.models.schemas import CallStartRequest, AudioInjectRequest
from pydantic import ValidationError


def test_get_settings():
    """Test settings retrieval."""
    settings = get_settings()
    assert settings.HOST is not None
    assert settings.PORT is not None
    assert settings.DEFAULT_CALL_DURATION > 0
    assert settings.MAX_CALL_DURATION > 0


def test_get_project_root():
    """Test project root path."""
    root = get_project_root()
    assert root.exists()
    assert root.is_dir()


def test_call_start_request_valid():
    """Test valid call start request."""
    request = CallStartRequest(
        destination="sip:test@example.com",
        duration=60
    )
    assert request.destination == "sip:test@example.com"
    assert request.duration == 60


def test_call_start_request_invalid_destination():
    """Test call start request with invalid destination."""
    with pytest.raises(ValidationError):
        CallStartRequest(destination="invalid")


def test_call_start_request_invalid_duration():
    """Test call start request with invalid duration."""
    with pytest.raises(ValidationError):
        CallStartRequest(
            destination="sip:test@example.com",
            duration=500  # Exceeds max
        )


def test_audio_inject_request_valid():
    """Test valid audio inject request."""
    request = AudioInjectRequest(audio_file_name="test.wav")
    assert request.audio_file_name == "test.wav"


def test_audio_inject_request_invalid_extension():
    """Test audio inject request with invalid extension."""
    with pytest.raises(ValidationError):
        AudioInjectRequest(audio_file_name="test.mp3")


def test_audio_inject_request_path_traversal():
    """Test audio inject request prevents path traversal."""
    with pytest.raises(ValidationError):
        AudioInjectRequest(audio_file_name="../test.wav")
    
    with pytest.raises(ValidationError):
        AudioInjectRequest(audio_file_name="../../etc/passwd.wav")

