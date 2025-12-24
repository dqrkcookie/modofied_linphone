"""
API routes for Linphone Caller.
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from ..models.schemas import (
    CallStartRequest, CallStartResponse,
    CallStatusResponse, AudioInjectRequest, AudioInjectResponse,
    CallEndResponse, CallInfo,
    HealthResponse, ErrorResponse
)
from ..core.linphone_controller import get_controller
from ..core.config import get_audio_directory


router = APIRouter(prefix="/api/v1", tags=["calls"])


@router.post(
    "/call/start",
    response_model=CallStartResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Start a new call",
    description="Initiate a new outbound call to the specified SIP destination. Only ONE call can be active at a time."
)
async def start_call(request: CallStartRequest):
    """Start a new call."""
    try:
        controller = get_controller()
        call = await controller.start_call(
            destination=request.destination,
            duration=request.duration,
            auto_play_audio=request.audio_file,
            play_after_seconds=request.play_after_seconds
        )
        
        return CallStartResponse(
            status=call.status,
            call_id=call.call_id,
            destination=call.destination,
            started_at=call.started_at,
            duration_limit=call.duration_limit,
            log_file=call.logger.get_log_path(),
            message="Call initiated successfully"
        )
    except ValueError as e:
        # A call is already in progress
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except FileNotFoundError as e:
        # Audio file not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Runtime error starting call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting call: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/call/status",
    response_model=CallStatusResponse,
    responses={
        404: {"model": ErrorResponse}
    },
    summary="Get call status",
    description="Retrieve the current status and details of the active call"
)
async def get_call_status():
    """Get status of the current call."""
    controller = get_controller()
    call = controller.get_current_call()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active call"
        )
    
    return CallStatusResponse(
        status=call.status,
        destination=call.destination,
        started_at=call.started_at,
        duration=call.get_duration(),
        duration_limit=call.duration_limit,
        current_audio=call.current_audio
    )


@router.post(
    "/call/playAudio",
    response_model=AudioInjectResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    },
    summary="Play audio into call",
    description="Play an audio file into the active call"
)
async def play_audio(request: AudioInjectRequest):
    """Play audio into the active call."""
    try:
        controller = get_controller()
        await controller.inject_audio(
            request.audio_file,
            silence_after_seconds=request.silence_after_seconds
        )
        
        call = controller.get_current_call()
        
        return AudioInjectResponse(
            call_id=call.call_id,
            status=call.status,
            audio_file=request.audio_file,
            log_file=call.logger.get_log_path(),
            message="Audio injection started successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error injecting audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/call/end",
    response_model=CallEndResponse,
    responses={
        404: {"model": ErrorResponse}
    },
    summary="End a call",
    description="Terminate the active call"
)
async def end_call():
    """End the active call."""
    try:
        controller = get_controller()
        call = controller.get_current_call()
        
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active call to end"
            )
        
        # Capture call details before ending
        call_id = call.call_id
        log_file = call.logger.get_log_path()
        duration = call.get_duration()
        
        # End the call
        await controller.end_call()
        
        return CallEndResponse(
            call_id=call_id,
            status=call.status,
            duration=duration,
            log_file=log_file,
            message="Call ended successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/call/info",
    response_model=CallInfo,
    summary="Get current call info",
    description="Get information about the current active call (if any)"
)
async def get_call_info():
    """Get information about the current call."""
    controller = get_controller()
    call = controller.get_current_call()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active call"
        )
    
    return CallInfo(**call.to_info())


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the service and linphone are available"
)
async def health_check():
    """Health check endpoint."""
    controller = get_controller()
    linphone_available = await controller.check_linphone_available()
    
    # Check audio directory
    audio_dir = get_audio_directory()
    audio_accessible = audio_dir.exists() and audio_dir.is_dir()
    
    # Check if there's an active call
    has_active_call = controller.has_active_call()
    
    return HealthResponse(
        status="healthy" if linphone_available and audio_accessible else "degraded",
        linphone_available=linphone_available,
        timestamp=datetime.utcnow(),
        audio_directory_accessible=audio_accessible,
        has_active_call=has_active_call
    )

