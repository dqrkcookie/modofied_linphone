"""
Linphone controller for managing calls and audio injection.
"""
import asyncio
import os
import re
import shutil
import uuid
import wave
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger

from ..models.schemas import CallStatus
from .config import get_settings, get_audio_directory
from .call_logger import CallLogger


class Call:
    """Represents the active call (only ONE call supported at a time)."""
    
    def __init__(self, destination: str, duration_limit: int, 
                 auto_play_audio: Optional[str] = None, 
                 play_after_seconds: int = 0):
        self.call_id = str(uuid.uuid4())
        self.destination = destination
        self.status = CallStatus.INITIATED
        self.started_at = datetime.utcnow()
        self.duration_limit = duration_limit
        self.process: Optional[asyncio.subprocess.Process] = None
        self.current_audio: Optional[str] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self.linphone_call_id: Optional[int] = None  # Track linphone's internal call ID
        
        # Auto-play audio feature
        self.auto_play_audio = auto_play_audio
        self.play_after_seconds = play_after_seconds
        self._auto_play_triggered = False  # Track if auto-play already happened
        
        # Create per-call logger
        self.logger = CallLogger(destination, self.call_id)
        
        # Log call initialization with clear separator
        self.logger.info("=" * 60)
        self.logger.info(f"🆕 NEW CALL STARTED {destination}")
        self.logger.info("=" * 60)
        self.logger.info(f"Call initialized", 
                        destination=destination,
                        duration_limit=duration_limit,
                        auto_play_audio=auto_play_audio or "none",
                        play_after_seconds=play_after_seconds if auto_play_audio else "n/a")
    
    def update_status(self, new_status: CallStatus):
        """Update call status and log the change."""
        old_status = self.status
        self.status = new_status
        if old_status != new_status:
            self.logger.log_state_change(old_status.value, new_status.value)
        
    def get_duration(self) -> int:
        """Get current call duration in seconds."""
        return int((datetime.utcnow() - self.started_at).total_seconds())
    
    def is_active(self) -> bool:
        """Check if call is still active."""
        return self.status in [CallStatus.ACTIVE, CallStatus.PLAYING_AUDIO, CallStatus.RINGING]
    
    def to_info(self) -> dict:
        """Convert call to CallInfo dict."""
        return {
            "call_id": self.call_id,
            "status": self.status,
            "destination": self.destination,
            "started_at": self.started_at,
            "duration": self.get_duration(),
            "duration_limit": self.duration_limit,
            "log_file": self.logger.get_log_path()
        }
    
    def finalize(self):
        """Finalize call and write summary."""
        self.logger.log_summary(datetime.utcnow(), self.status.value)


def get_audio_duration(audio_path: Path) -> float:
    """
    Calculate the duration of a WAV audio file in seconds.
    
    Args:
        audio_path: Path to the WAV file
        
    Returns:
        Duration in seconds (float)
        
    Raises:
        Exception: If file cannot be read or is not a valid WAV
    """
    try:
        with wave.open(str(audio_path), 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        logger.warning(f"Could not determine audio duration for {audio_path.name}: {e}")
        # Return a conservative estimate if we can't read the file
        return 5.0  # Default 5 seconds


class LinphoneController:
    """Controller for managing Linphone calls (ONE call at a time only)."""
    
    def __init__(self):
        self.settings = get_settings()
        self.current_call: Optional[Call] = None
        self._linphone_available: Optional[bool] = None
        self._current_audio_task: Optional[asyncio.Task] = None  # Track current background audio task
        
    async def check_linphone_available(self) -> bool:
        """Check if linphonec is available."""
        if self._linphone_available is not None:
            return self._linphone_available
            
        try:
            # Check if linphonec binary exists
            linphone_bin = self.settings.LINPHONE_BINARY
            if shutil.which(linphone_bin.split('/')[-1]) or shutil.which('linphonec'):
                self._linphone_available = True
                logger.info("Linphone (linphonec) is available")
            else:
                self._linphone_available = False
                logger.error("linphonec not found")
            return self._linphone_available
        except Exception as e:
            logger.error(f"Error checking linphone availability: {e}")
            self._linphone_available = False
            return False
    
    async def start_call(self, destination: str, duration: Optional[int] = None,
                        auto_play_audio: Optional[str] = None,
                        play_after_seconds: int = 0) -> Call:
        """
        Start a new call.
        
        Args:
            destination: SIP URI of the destination
            duration: Call duration in seconds (None = use default)
            auto_play_audio: Optional audio file to play after call is answered
            play_after_seconds: Delay in seconds before playing audio after answered
            
        Returns:
            Call object
        
        Raises:
            ValueError: If a call is already in progress
            FileNotFoundError: If audio file specified but not found
        """
        if not await self.check_linphone_available():
            raise RuntimeError("Linphone is not available")
        
        # Check if a call is already active
        if self.current_call and self.current_call.is_active():
            raise ValueError(
                f"A call is already in progress to {self.current_call.destination}. "
                "End the current call before starting a new one."
            )
        
        # Validate audio file if specified
        if auto_play_audio:
            audio_path = get_audio_directory() / auto_play_audio
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {auto_play_audio}")
        
        # Validate and set duration
        if duration is None:
            duration = self.settings.DEFAULT_CALL_DURATION
        else:
            duration = min(duration, self.settings.MAX_CALL_DURATION)
        
        # Create call object
        call = Call(destination, duration, auto_play_audio, play_after_seconds)
        self.current_call = call
        
        call.logger.info(f"Starting call", 
                        destination=destination,
                        duration_limit=duration)
        
        try:
            linphone_bin = self.settings.LINPHONE_BINARY
            linphone_config = self._get_linphone_config_path()
            
            # CRITICAL: Clean up old Linphone database to ensure new config is used
            # The old database at ~/.local/share/linphone/ can be locked and prevent new config from loading
            old_db_path = Path.home() / ".local" / "share" / "linphone"
            if old_db_path.exists():
                call.logger.warning(f"🗑️  Removing old Linphone database to ensure clean start: {old_db_path}")
                try:
                    shutil.rmtree(old_db_path)
                    call.logger.info(f"✓ Old database removed")
                except Exception as e:
                    call.logger.warning(f"Could not remove old database: {e}")
            
            # Ensure tmp directories exist for new database with proper structure
            tmp_linphone_dir = Path("/tmp/linphone")
            tmp_cache_dir = Path("/tmp/linphone-cache")
            for tmp_dir in [tmp_linphone_dir, tmp_cache_dir]:
                tmp_dir.mkdir(parents=True, exist_ok=True)
                call.logger.info(f"✓ Ensured directory exists: {tmp_dir}")
            
            # Clean up any stale database files in tmp to ensure fresh start
            db_file = tmp_linphone_dir / "linphone.db"
            if db_file.exists():
                try:
                    db_file.unlink()
                    call.logger.info(f"✓ Removed stale database file: {db_file}")
                except Exception as e:
                    call.logger.warning(f"Could not remove stale database: {e}")
            
            # Set LINPHONERC environment variable for config
            env = os.environ.copy()
            env['LINPHONERC'] = str(linphone_config)
            
            # Force Linphone to use temp directories
            env['LC_HOME'] = str(tmp_linphone_dir)
            
            # Verify linphonec exists
            if not shutil.which(linphone_bin.split('/')[-1]):
                console_path = shutil.which('linphonec')
                if console_path:
                    linphone_bin = console_path
                else:
                    raise FileNotFoundError(
                        "linphonec not found. Please install: "
                        "sudo apt-get install -y linphone-cli"
                    )
            
            # Start linphonec process
            # Use explicit --db parameter to override database path
            cmd = [
                linphone_bin, 
                '-c', str(linphone_config),
                '--db', '/tmp/linphone/linphone.db'  # Explicit database location
            ]
            call.logger.info(f"📞 Starting linphonec: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                env=env
            )
            
            call.process = process
            
            # Start reading output streams
            asyncio.create_task(self._read_linphone_output(call))
            asyncio.create_task(self._read_linphone_stderr(call))
            
            # Wait for linphonec to initialize and register to SIP server
            # Increased from 2s to 5s to allow time for SIP registration
            call.logger.info("⏳ Waiting for Linphone to initialize and register to SIP server...")
            await asyncio.sleep(5)
            
            # Check registration status by requesting info
            if process.stdin and not process.stdin.is_closing():
                call.logger.info("📋 Checking SIP registration status...")
                process.stdin.write(b"info\n")
                await process.stdin.drain()
                await asyncio.sleep(1)
            
            # Check if process is still alive
            if process.returncode is not None:
                raise RuntimeError(f"Linphonec died immediately with code {process.returncode}")
            
            # Verify stdin is open
            if process.stdin.is_closing():
                raise RuntimeError("Linphonec stdin closed - process may have crashed")
            
            # IMPORTANT: Enable file mode BEFORE making the call
            # This allows 'play' command to work for audio injection
            call.logger.info("📡 Enabling file mode for audio playback")
            soundcard_cmd = "soundcard use files\n"
            process.stdin.write(soundcard_cmd.encode())
            await process.stdin.drain()
            await asyncio.sleep(0.5)  # Wait for mode switch
            
            # Stop background audio/comfort noise by playing silence
            call.logger.info("🔇 Stopping background audio")
            silence_cmd = "play /dev/zero\n"
            process.stdin.write(silence_cmd.encode())
            await process.stdin.drain()
            await asyncio.sleep(0.3)  # Brief pause
            
            # Send call command via stdin
            # linphonec uses: call <destination>
            call_command = f"call {destination}\n"
            call.logger.info(f"📞 Sending call command: call {destination}")
            process.stdin.write(call_command.encode())
            await process.stdin.drain()
            
            # Wait a bit for call to start
            await asyncio.sleep(0.5)
            
            # Status will be updated by _read_linphone_output based on actual linphone messages
            # Don't force RINGING here - let linphone tell us the actual state
            
            # Start monitoring task
            call._monitor_task = asyncio.create_task(
                self._monitor_call(call)
            )
            
            call.logger.info(f"Call initiated successfully")
            return call
            
        except Exception as e:
            call.logger.error(f"Error starting call: {e}")
            call.update_status(CallStatus.FAILED)
            raise
    
    async def _monitor_call(self, call: Call):
        """
        Monitor call duration and terminate when limit is reached.
        Also detects when call ends externally (remote hangup).
        
        Args:
            call: Call object to monitor
        """
        try:
            # Monitor duration - check every second
            while call.is_active() and call.get_duration() < call.duration_limit:
                await asyncio.sleep(1)
            
            # End call if duration limit reached
            if call.is_active():
                call.logger.info(f"Duration limit reached ({call.duration_limit}s), ending call")
                await self.end_call()
            elif call.status == CallStatus.TERMINATED:
                # Call was terminated externally (remote hangup detected)
                call.logger.info(f"Call ended externally, cleaning up linphonec process")
                await self.end_call()
            elif call.status == CallStatus.FAILED:
                # Call failed (declined, busy, error, etc.)
                call.logger.info(f"Call failed, cleaning up linphonec process")
                await self.end_call()
                
        except asyncio.CancelledError:
            call.logger.info(f"Monitor task cancelled")
        except Exception as e:
            call.logger.error(f"Error monitoring call: {e}")
    
    async def _auto_play_audio_after_delay(self, call: Call):
        """
        Auto-play audio after specified delay once call is answered.
        
        Args:
            call: Call object with auto_play_audio configured
        """
        try:
            if call.play_after_seconds > 0:
                call.logger.info(
                    f"⏱️  Waiting {call.play_after_seconds}s before auto-playing: {call.auto_play_audio}"
                )
                await asyncio.sleep(call.play_after_seconds)
            
            # Check if call is still active
            if not call.is_active():
                call.logger.info(f"Call ended before auto-play audio could start")
                return
            
            call.logger.info(f"🎵 Auto-playing audio: {call.auto_play_audio}")
            await self.inject_audio(call.auto_play_audio)
            
        except FileNotFoundError as e:
            call.logger.error(f"Auto-play audio file not found: {e}")
        except Exception as e:
            call.logger.error(f"Error auto-playing audio: {e}")
    
    async def _read_linphone_output(self, call: Call):
        """Read and log linphone stdout and update call status based on actual events."""
        try:
            if call.process and call.process.stdout:
                async for line in call.process.stdout:
                    output = line.decode().strip()
                    if output:
                        call.logger.log_linphone_output(output)
                        
                        # Extract linphone call ID from output
                        call_id_match = re.search(r'Call\s+(\d+)', output)
                        if call_id_match and call.linphone_call_id is None:
                            call.linphone_call_id = int(call_id_match.group(1))
                            call.logger.info(f"📞 Detected linphone call ID: {call.linphone_call_id}")
                            # When Call ID is detected, call is actually being made
                            if call.status == CallStatus.INITIATED:
                                call.update_status(CallStatus.RINGING)
                                call.logger.info(f"🔔 Call detected as ringing")
                        
                        # Parse linphonec text-based output
                        lower_output = output.lower()
                        
                        if "ringing" in lower_output or "in progress" in lower_output:
                            # Call is ringing at destination
                            if call.status == CallStatus.INITIATED:
                                call.update_status(CallStatus.RINGING)
                            call.logger.info(f"🔔 Call ringing")
                        
                        elif "connected" in lower_output or "ok" in lower_output:
                            # Call connected
                            call.logger.info(f"✓ Call connected")
                            if call.status in [CallStatus.INITIATED, CallStatus.RINGING]:
                                call.update_status(CallStatus.ACTIVE)
                                
                                # Trigger auto-play audio if configured (on connected)
                                if call.auto_play_audio and not call._auto_play_triggered:
                                    call._auto_play_triggered = True
                                    asyncio.create_task(
                                        self._auto_play_audio_after_delay(call)
                                    )
                        
                        elif "media streams established" in lower_output:
                            # Media streams established (call is definitely active)
                            call.logger.info(f"✓ Media streams established")
                            if call.status != CallStatus.ACTIVE:
                                call.update_status(CallStatus.ACTIVE)
                                
                                # Trigger auto-play audio if configured (backup trigger)
                                if call.auto_play_audio and not call._auto_play_triggered:
                                    call._auto_play_triggered = True
                                    asyncio.create_task(
                                        self._auto_play_audio_after_delay(call)
                                    )
                        
                        elif "declined" in lower_output or "busy" in lower_output:
                            # Call was declined or busy
                            call.logger.warning(f"❌ Call declined or busy")
                            call.update_status(CallStatus.FAILED)
                        
                        elif "ended" in lower_output:
                            # Call ended - could be normal or remote hangup
                            if "unknown error" in lower_output:
                                # "Unknown error" typically means remote party hung up
                                call.logger.info(f"📞 Call ended by remote party")
                            else:
                                call.logger.info(f"📞 Call ended")
                            
                            # Update status to terminated (call is over)
                            call.update_status(CallStatus.TERMINATED)
                            
                            # Schedule cleanup (can't await here as we're in a loop)
                            # The monitor task will see status changed and exit
                            # Then end_call() will be called to cleanup the process
                        
                        elif "failed" in lower_output or "cannot" in lower_output:
                            # Only mark as failed if it's a real error (not just a linphone internal message)
                            if "cannot" in lower_output and "understand" not in lower_output:
                                call.logger.error(f"❌ Call failed: {output}")
                                call.update_status(CallStatus.FAILED)
                                
                                # Schedule cleanup (can't await here as we're in a loop)
                                # The monitor task will see status changed and exit
                                # Then end_call() will be called to cleanup the process
        
        except Exception as e:
            call.logger.warning(f"Error reading linphone output: {e}")
    
    async def _read_linphone_stderr(self, call: Call):
        """Read and log linphone stderr for errors."""
        try:
            if call.process and call.process.stderr:
                async for line in call.process.stderr:
                    error = line.decode().strip()
                    if error:
                        call.logger.log_linphone_error(error)
        except Exception as e:
            call.logger.warning(f"Error reading linphone stderr: {e}")
    
    async def _play_audio_with_silence_background(self, call: Call, audio_path: Path, 
                                                    audio_file_name: str, silence_after_seconds: float):
        """
        Background task to wait for audio playback completion and add silence gap.
        Runs asynchronously without blocking the API response.
        Can be cancelled if new audio is requested (interruption behavior).
        
        Args:
            call: The active call object
            audio_path: Path to the audio file
            audio_file_name: Name of the audio file (for logging)
            silence_after_seconds: Duration of silence gap to add
        """
        try:
            # Calculate audio duration
            audio_duration = get_audio_duration(audio_path)
            
            # Wait for audio to finish playing (duration + small buffer)
            await asyncio.sleep(audio_duration + 0.2)
            call.logger.info(f"✓ Audio playback completed: {audio_file_name}")
            
            # Add silence gap after audio to create RTP stream break
            if silence_after_seconds > 0 and call.process:
                silence_file = get_audio_directory() / "silence.wav"
                if silence_file.exists():
                    call.logger.info(f"🔇 Adding {silence_after_seconds}s silence gap for RTP segmentation")
                    
                    # Play silence for the specified duration
                    silence_iterations = int(silence_after_seconds)
                    for i in range(silence_iterations):
                        # Check if process is still alive
                        if not call.process or call.process.returncode is not None:
                            call.logger.warning(f"Call ended before silence gap completed")
                            return
                        
                        if call.process.stdin and not call.process.stdin.is_closing():
                            silence_cmd = f"play {silence_file.resolve()}\n"
                            call.process.stdin.write(silence_cmd.encode())
                            await call.process.stdin.drain()
                            await asyncio.sleep(1.0)
                    
                    # Add any remaining fractional seconds
                    remaining_silence = silence_after_seconds - silence_iterations
                    if remaining_silence > 0:
                        await asyncio.sleep(remaining_silence)
                    
                    call.logger.info(f"✓ Silence gap completed")
                else:
                    call.logger.warning(f"silence.wav not found, using sleep fallback for {silence_after_seconds}s")
                    await asyncio.sleep(silence_after_seconds)
            
            # Restore status to active
            if call.status == CallStatus.PLAYING_AUDIO:
                call.update_status(CallStatus.ACTIVE)
            
            call.logger.info(f"✓ Audio injection completed with silence gap")
            
        except asyncio.CancelledError:
            # Task was cancelled because new audio was requested
            call.logger.info(f"⏭️  Audio interrupted: {audio_file_name} (new audio requested)")
            raise  # Re-raise to properly cancel the task
        except Exception as e:
            call.logger.error(f"Error in background audio playback: {e}")
            if call.status == CallStatus.PLAYING_AUDIO:
                call.update_status(CallStatus.ACTIVE)
    
    async def inject_audio(self, audio_file_name: str, silence_after_seconds: float = 1.5) -> None:
        """
        Inject audio into the active call using linphonec's play command.
        
        This method returns immediately after starting audio playback.
        The audio playback and silence gap happen in the background.
        
        **Interruption Behavior**: If audio is currently playing, it will be 
        interrupted and replaced with the new audio immediately. This ensures
        the most recent audio request always plays without delay.
        
        Requires 'soundcard use files' to be set before call (done automatically).
        Supports multiple audio injections in the same call without crashes.
        
        After playing the audio, injects a silence gap to ensure proper RTP stream
        segmentation for transcription systems.

        Args:
            audio_file_name: Name of the audio file to play
            silence_after_seconds: Duration of silence to add after audio (default: 1.5s)
                                   This creates a gap in the RTP stream, allowing transcription
                                   systems to treat each audio as a separate utterance.

        Raises:
            ValueError: If no call is active
            FileNotFoundError: If audio file not found
            RuntimeError: If linphone process is not available
        """
        if not self.current_call:
            raise ValueError("No active call to inject audio into")

        if not self.current_call.is_active():
            raise ValueError("Current call is not active")

        # Get audio file path
        audio_path = get_audio_directory() / audio_file_name
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_name}")

        call = self.current_call
        call.logger.log_audio_injection(audio_file_name)

        # Check if linphone process is still alive
        if not call.process or call.process.returncode is not None:
            raise RuntimeError("Linphonec has crashed or terminated")
        
        # Check if stdin is still available
        if not call.process.stdin or call.process.stdin.is_closing():
            raise RuntimeError("Linphonec stdin is not available")
        
        # Cancel any currently playing audio task (interrupt previous audio)
        if self._current_audio_task and not self._current_audio_task.done():
            call.logger.info(f"⏭️  Interrupting current audio to play: {audio_file_name}")
            self._current_audio_task.cancel()
            try:
                await self._current_audio_task  # Wait for cancellation to complete
            except asyncio.CancelledError:
                pass  # Expected
        
        # Update status
        call.update_status(CallStatus.PLAYING_AUDIO)
        call.current_audio = audio_file_name

        # Use absolute path for the audio file
        absolute_audio_path = audio_path.resolve()
        
        # Calculate audio duration for logging
        audio_duration = get_audio_duration(audio_path)
        call.logger.info(f"🎵 Playing: {audio_file_name} (duration: {audio_duration:.2f}s + {silence_after_seconds}s silence)")
        
        # Send play command immediately (this interrupts any currently playing audio in linphonec)
        play_cmd = f"play {absolute_audio_path}\n"
        call.process.stdin.write(play_cmd.encode())
        await call.process.stdin.drain()
        
        # Start background task to wait for completion and add silence
        self._current_audio_task = asyncio.create_task(
            self._play_audio_with_silence_background(call, audio_path, audio_file_name, silence_after_seconds)
        )
        
        # Return immediately - audio plays in background
        call.logger.info(f"✓ Audio started (playing in background)")
    
    async def end_call(self) -> None:
        """
        End the active call.
        
        Raises:
            ValueError: If no call is active
        """
        if not self.current_call:
            raise ValueError("No active call to end")
        
        call = self.current_call
        
        # Prevent double-execution if called multiple times
        if call.status == CallStatus.TERMINATED:
            call.logger.info(f"Call already terminated, ensuring cleanup")
            # Even if status is terminated, ensure process is killed and current_call is cleared
            if call.process and call.process.returncode is None:
                try:
                    call.logger.warning(f"Process still running after termination, attempting graceful exit first")
                    
                    # Try graceful shutdown first (terminate + quit)
                    if call.process.stdin and not call.process.stdin.is_closing():
                        try:
                            call.logger.info(f"🛑 Sending terminate command to linphone")
                            call.process.stdin.write(b"terminate\n")
                            await call.process.stdin.drain()
                            await asyncio.sleep(0.3)
                            call.logger.info(f"🛑 Sending quit command to linphone")
                            call.process.stdin.write(b"quit\n")
                            await call.process.stdin.drain()
                            
                            # Wait briefly for graceful exit
                            await asyncio.wait_for(call.process.wait(), timeout=2.0)
                            call.logger.info(f"✓ Zombie process exited gracefully")
                        except (asyncio.TimeoutError, BrokenPipeError, Exception):
                            # Graceful exit failed, force kill
                            call.logger.warning(f"Graceful exit failed, force killing process")
                            call.process.kill()
                            await call.process.wait()
                            call.logger.info(f"✓ Zombie process force killed")
                    else:
                        # stdin not available, force kill immediately
                        call.logger.warning(f"stdin not available, force killing process")
                        call.process.kill()
                        await call.process.wait()
                        call.logger.info(f"✓ Zombie process force killed")
                        
                except Exception as e:
                    call.logger.error(f"Error killing zombie process: {e}")
                    # Last resort - try kill without waiting
                    try:
                        call.process.kill()
                        call.logger.info(f"✓ Zombie process force killed")
                    except:
                        pass
            
            # Clear current call reference and audio task
            self.current_call = None
            self._current_audio_task = None
            return
        
        call.logger.info(f"Ending call")
        
        try:
            # Cancel monitor task
            if call._monitor_task:
                call._monitor_task.cancel()
                try:
                    await call._monitor_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel any ongoing audio playback task
            if self._current_audio_task and not self._current_audio_task.done():
                call.logger.info(f"Cancelling ongoing audio playback")
                self._current_audio_task.cancel()
                try:
                    await self._current_audio_task
                except asyncio.CancelledError:
                    pass
            self._current_audio_task = None
            
            # Send terminate command to the active linphone process via stdin
            if call.process and call.process.stdin:
                try:
                    # Check if process is still alive
                    if call.process.returncode is None:
                        call.logger.info(f"🛑 Sending terminate command to linphone")
                        call.process.stdin.write(b"terminate\n")
                        await call.process.stdin.drain()
                        
                        # Send quit to exit linphone cleanly
                        await asyncio.sleep(0.5)
                        call.logger.info(f"🛑 Sending quit command to linphone")
                        call.process.stdin.write(b"quit\n")
                        await call.process.stdin.drain()
                        
                        # Wait for process to terminate
                        await asyncio.wait_for(call.process.wait(), timeout=3.0)
                        call.logger.info(f"✓ Linphone process terminated cleanly")
                    else:
                        call.logger.info(f"Linphone process already exited with code {call.process.returncode}")
                except asyncio.TimeoutError:
                    call.logger.warning(f"Timeout waiting for linphone to terminate, killing process")
                    call.process.kill()
                    await call.process.wait()
                except Exception as e:
                    call.logger.warning(f"Error terminating linphone process: {e}")
                    if call.process and call.process.returncode is None:
                        try:
                            call.process.kill()
                            await call.process.wait()
                        except:
                            pass
            
            # Update status
            call.update_status(CallStatus.TERMINATED)
            call.logger.info(f"✓ Call ended successfully")
            
            # Finalize call log
            call.finalize()
            
            # Clear current call reference and audio task to allow new calls
            self.current_call = None
            self._current_audio_task = None
            
        except Exception as e:
            logger.error(f"Error ending call to {call.destination}: {e}")
            call.status = CallStatus.FAILED
            # Even on error, clear current_call and audio task to prevent blocking future calls
            self.current_call = None
            self._current_audio_task = None
            raise
    
    def get_current_call(self) -> Optional[Call]:
        """Get the current active call."""
        return self.current_call
    
    def has_active_call(self) -> bool:
        """Check if there is an active call."""
        return self.current_call is not None and self.current_call.is_active()
    
    def _get_linphone_config_path(self) -> Path:
        """Get path to linphone config file."""
        from .config import get_config_directory
        return get_config_directory() / "linphonerc"


# Global controller instance
_controller: Optional[LinphoneController] = None


def get_controller() -> LinphoneController:
    """Get global linphone controller instance."""
    global _controller
    if _controller is None:
        _controller = LinphoneController()
    return _controller

