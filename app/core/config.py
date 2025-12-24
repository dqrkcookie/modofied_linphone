"""
Core configuration management for Linphone Caller application.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with default values."""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    WORKERS: int = 1
    
    # Call Settings
    DEFAULT_CALL_DURATION: int = 120  # seconds
    MAX_CALL_DURATION: int = 300  # seconds
    AUDIO_DIRECTORY: str = "assets/audio"
    
    # Linphone Settings
    LINPHONE_CONFIG_DIR: str = "config"
    LINPHONE_BINARY: str = "/usr/bin/linphonec"
    
    # Optional API Authentication
    API_KEY: Optional[str] = None
    
    class Config:
        # Allow environment variables to override if needed
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        # Don't fail if .env doesn't exist
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_audio_directory() -> Path:
    """Get the audio files directory."""
    settings = get_settings()
    return get_project_root() / settings.AUDIO_DIRECTORY


def get_log_directory() -> Path:
    """Get the logs directory."""
    return get_project_root() / "logs"


def get_config_directory() -> Path:
    """Get the configuration directory."""
    settings = get_settings()
    return get_project_root() / settings.LINPHONE_CONFIG_DIR


def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        get_audio_directory(),
        get_log_directory(),
        get_config_directory(),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

