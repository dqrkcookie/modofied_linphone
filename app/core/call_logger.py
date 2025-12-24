"""
Per-call logging functionality.
Each call gets its own detailed log file.
"""
from datetime import datetime
from pathlib import Path
from loguru import logger


class CallLogger:
    """Logger for individual call sessions."""
    
    def __init__(self, destination: str, call_id: str):
        """
        Initialize call logger.
        
        Args:
            destination: SIP URI destination
            call_id: Unique call identifier
        """
        self.destination = destination
        self.call_id = call_id
        self.start_time = datetime.now()
        
        # Create call logs directory
        self.logs_dir = Path("logs/calls")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp and call_id
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        # Sanitize destination for filename (remove special chars)
        safe_dest = destination.replace("sip:", "").replace("@", "_at_").replace(":", "_")
        self.log_file = self.logs_dir / f"call_{timestamp}_{safe_dest}_{call_id[:8]}.log"
        
        # Initialize log file
        self._write_header()
    
    def _write_header(self):
        """Write log file header with call information."""
        with open(self.log_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("LINPHONE CALL LOG\n")
            f.write("=" * 80 + "\n")
            f.write(f"Call ID:      {self.call_id}\n")
            f.write(f"Destination:  {self.destination}\n")
            f.write(f"Started:      {self.start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
            f.write("=" * 80 + "\n\n")
    
    def log(self, level: str, message: str, **kwargs):
        """
        Log a message to both main log and call-specific log.
        
        Args:
            level: Log level (INFO, DEBUG, WARNING, ERROR)
            message: Log message
            **kwargs: Additional key-value pairs to log
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Format message with kwargs
        if kwargs:
            extra = " | " + " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message}{extra}"
        else:
            full_message = message
        
        # Write to call-specific log file
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [{level:8s}] {full_message}\n")
        
        # Also log to main application log
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(f"[Call {self.call_id[:8]}] {full_message}")
    
    def info(self, message: str, **kwargs):
        """Log INFO level message."""
        self.log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log WARNING level message."""
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log ERROR level message."""
        self.log("ERROR", message, **kwargs)
    
    def log_state_change(self, old_state: str, new_state: str):
        """Log call state transition."""
        self.info(f"State changed: {old_state} → {new_state}")
    
    def log_linphone_output(self, line: str):
        """Log output from linphone process."""
        self.info(f"[Linphone] {line}")
    
    def log_linphone_error(self, line: str):
        """Log error output from linphone process."""
        self.error(f"[Linphone Error] {line}")
    
    def log_audio_injection(self, audio_file: str):
        """Log audio injection event."""
        self.info(f"Injecting audio: {audio_file}")
    
    def log_summary(self, end_time: datetime, final_status: str):
        """Write call summary at the end."""
        duration = (end_time - self.start_time).total_seconds()
        
        with open(self.log_file, 'a') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("CALL SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Call ID:       {self.call_id}\n")
            f.write(f"Destination:   {self.destination}\n")
            f.write(f"Started:       {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Ended:         {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration:      {duration:.2f} seconds\n")
            f.write(f"Final Status:  {final_status}\n")
            f.write("=" * 80 + "\n")
        
        self.info(f"Call ended", 
                  duration=f"{duration:.2f}s",
                  status=final_status,
                  log_file=str(self.log_file))
    
    def get_log_path(self) -> str:
        """Get the path to the call log file."""
        return str(self.log_file)

