"""
Pydantic models for request/response schemas.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class CallStatus(str, Enum):
    """Call status enumeration."""
    INITIATED = "initiated"
    RINGING = "ringing"
    ACTIVE = "active"
    PLAYING_AUDIO = "playing_audio"
    ENDED = "ended"
    FAILED = "failed"
    TERMINATED = "terminated"


class CallStartRequest(BaseModel):
    """Request model for starting a call."""
    destination: str = Field(
        ..., 
        description="SIP URI of the destination (e.g., sip:user@domain.com)",
        example="sip:1234567890@sip.example.com"
    )
    duration: Optional[int] = Field(
        None, 
        description="Call duration in seconds (max 900, default 120)",
        ge=1,
        le=900
    )
    audio_file: Optional[str] = Field(
        None,
        description="Optional audio file to play after call is answered",
        example="greeting.wav"
    )
    play_after_seconds: Optional[int] = Field(
        0,
        description="Delay in seconds before playing audio after call is answered (default 0)",
        ge=0,
        le=60
    )
    
    @validator('destination')
    def validate_destination(cls, v):
        """Validate SIP URI format."""
        if not v.startswith('sip:'):
            raise ValueError('Destination must be a valid SIP URI starting with "sip:"')
        return v
    
    @validator('audio_file')
    def validate_audio_file(cls, v):
        """Validate audio file name."""
        if v is None:
            return v
        if not v.endswith('.wav'):
            raise ValueError('Audio file must be a .wav file')
        # Basic security check - no path traversal
        if '/' in v or '\\' in v or '..' in v:
            raise ValueError('Audio file name must not contain path separators')
        return v


class CallStartResponse(BaseModel):
    """Response model for call start."""
    status: CallStatus
    call_id: str = Field(description="Unique call identifier")
    destination: str
    started_at: datetime
    duration_limit: int = Field(description="Maximum call duration in seconds")
    log_file: str = Field(description="Path to call log file")
    message: Optional[str] = None


class CallStatusResponse(BaseModel):
    """Response model for call status."""
    status: CallStatus
    destination: str
    started_at: datetime
    duration: int = Field(description="Current call duration in seconds")
    duration_limit: int = Field(description="Maximum call duration in seconds")
    current_audio: Optional[str] = None


class AudioInjectRequest(BaseModel):
    """Request model for audio injection."""
    audio_file: str = Field(
        ...,
        description="Name of the audio file in the assets/audio directory",
        example="greeting.wav"
    )
    silence_after_seconds: Optional[float] = Field(
        1.5,
        description="Duration of silence (in seconds) to add after audio for RTP stream segmentation (default: 1.5s). This ensures transcription systems treat each audio as a separate utterance.",
        ge=0,
        le=10
    )
    
    @validator('audio_file')
    def validate_audio_file(cls, v):
        """Validate audio file name."""
        if not v.endswith('.wav'):
            raise ValueError('Audio file must be a .wav file')
        # Basic security check - no path traversal
        if '/' in v or '\\' in v or '..' in v:
            raise ValueError('Audio file name must not contain path separators')
        return v


class AudioInjectResponse(BaseModel):
    """Response model for audio injection."""
    call_id: str = Field(description="Unique identifier for the call")
    status: CallStatus
    audio_file: str
    log_file: str = Field(description="Path to the detailed call log file")
    message: str


class CallEndResponse(BaseModel):
    """Response model for ending a call."""
    call_id: str = Field(description="Unique identifier for the call")
    status: CallStatus
    duration: int
    log_file: str = Field(description="Path to the detailed call log file")
    message: str


class CallInfo(BaseModel):
    """Information about the current call."""
    call_id: str = Field(description="Unique call identifier")
    status: CallStatus
    destination: str
    started_at: datetime
    duration: int
    duration_limit: int
    log_file: str = Field(description="Path to call log file")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    linphone_available: bool
    timestamp: datetime
    audio_directory_accessible: bool
    has_active_call: bool


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None

