# Linphone SIP Audio Injector

> 🎙️ **Production-ready HTTP API for injecting audio into active SIP calls using Linphone**

A robust, asynchronous Python API that enables real-time audio injection into SIP calls, perfect for IVR systems, automated voice assistants, call testing, and telecommunication applications.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

### 🎯 Core Capabilities
- ✅ **HTTP REST API** - Simple JSON API for making calls and injecting audio
- ✅ **Non-Blocking Audio Injection** - API returns immediately, audio plays in background
- ✅ **Interruption Support** - New audio automatically interrupts current playback
- ✅ **RTP Stream Segmentation** - Configurable silence gaps for proper transcription
- ✅ **Auto-Play on Answer** - Optionally play audio immediately when call connects
- ✅ **Multiple Formats** - Supports WAV files (8-48kHz, mono/stereo)
- ✅ **Unlimited Injections** - Inject audio as many times as needed per call
- ✅ **Call Management** - Start, monitor, inject audio, and end calls programmatically

### 🏗️ Architecture
- ✅ **Async/Await** - Built on asyncio for high performance
- ✅ **One Call at a Time** - Simple, predictable behavior
- ✅ **Process Management** - Robust linphonec process lifecycle control
- ✅ **Detailed Logging** - Per-call log files with full event history
- ✅ **Health Checks** - Built-in health monitoring endpoint
- ✅ **Production Ready** - Systemd service, deployment scripts, error handling

### 📊 Perfect For
- 🤖 **IVR Systems** - Interactive Voice Response automation
- 📞 **Call Testing** - Automated SIP call testing and validation
- 🎙️ **Voice Bots** - AI-powered voice assistants and chatbots
- 📈 **Call Centers** - Automated announcement and prompt systems
- 🧪 **Telecom Development** - SIP application testing and prototyping

---

## 🚀 Quick Start

### Prerequisites

- **Ubuntu 20.04+** or similar Linux distribution
- **Python 3.8+**
- **Linphone CLI** (`linphonec`)
- Network access to your SIP server

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/rathnavel/linphone-sip-audio-injector.git
cd linphone-sip-audio-injector
```

#### 2. Install Dependencies

```bash
# Install Linphone CLI
sudo apt update
sudo apt install -y linphone-cli

# Install Python dependencies
pip install -r requirements.txt
```

#### 3. Start the Server

```bash
# Development mode
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 4. Verify Installation

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "linphone_available": true,
  "timestamp": "2025-12-24T10:30:00.123Z",
  "audio_directory_accessible": true,
  "has_active_call": false
}
```

---

## 📖 Usage

### Basic Example: Make a Call and Inject Audio

```bash
# 1. Start a call
curl -X POST http://localhost:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1234@sip.example.com",
    "duration": 120
  }'

# 2. Wait for call to connect
sleep 3

# 3. Inject audio
curl -X POST http://localhost:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{
    "audio_file": "greeting.wav",
    "silence_after_seconds": 1.5
  }'

# 4. End the call
curl -X POST http://localhost:8000/api/v1/call/end
```

### Advanced Example: Auto-Play Audio on Answer

```bash
curl -X POST http://localhost:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1234@sip.example.com",
    "duration": 180,
    "audio_file": "welcome_message.wav",
    "play_after_seconds": 2
  }'
# Audio plays automatically 2 seconds after call connects
```

### Python Example

```python
import requests
import time

API_BASE = "http://localhost:8000/api/v1"

# Start call with auto-play
response = requests.post(f"{API_BASE}/call/start", json={
    "destination": "sip:1234@sip.example.com",
    "duration": 300,
    "audio_file": "greeting.wav",
    "play_after_seconds": 1
})

call_id = response.json()["call_id"]
print(f"Call started: {call_id}")

# Wait for greeting to finish
time.sleep(10)

# Inject multiple audio files
audio_files = ["question1.wav", "question2.wav", "question3.wav"]
for audio in audio_files:
    requests.post(f"{API_BASE}/call/playAudio", json={
        "audio_file": audio,
        "silence_after_seconds": 1.5
    })
    time.sleep(8)  # Wait for audio + silence

# End call
requests.post(f"{API_BASE}/call/end")
print("Call ended")
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/call/start` | Start a new SIP call |
| `GET` | `/call/status` | Get current call status |
| `POST` | `/call/playAudio` | Inject audio into active call |
| `POST` | `/call/end` | End the active call |

### Detailed API Documentation

#### `POST /call/start`

Start a new outbound SIP call.

**Request Body:**
```json
{
  "destination": "sip:1234@sip.example.com",
  "duration": 120,
  "audio_file": "greeting.wav",
  "play_after_seconds": 2
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `destination` | string | ✅ Yes | - | SIP URI (must start with `sip:`) |
| `duration` | integer | ❌ No | 120 | Max call duration in seconds (1-900, 15 minutes max) |
| `audio_file` | string | ❌ No | null | WAV file to auto-play after answer |
| `play_after_seconds` | integer | ❌ No | 0 | Delay before auto-play (0-60s) |

**Response (200 OK):**
```json
{
  "status": "ringing",
  "call_id": "a1b2c3d4-1234-5678-abcd-0123456789ab",
  "destination": "sip:1234@sip.example.com",
  "started_at": "2025-12-24T10:30:00.123Z",
  "duration_limit": 120,
  "log_file": "logs/calls/call_20251224_103000_1234_at_sip.example.com_a1b2c3d4.log",
  "message": "Call initiated successfully"
}
```

---

#### `POST /call/playAudio`

Inject audio into the active call. **Non-blocking** - returns immediately.

**Interruption Behavior:** If audio is currently playing, it will be interrupted and replaced with the new audio.

**Request Body:**
```json
{
  "audio_file": "menu_options.wav",
  "silence_after_seconds": 1.5
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `audio_file` | string | ✅ Yes | - | WAV file name in `assets/audio/` |
| `silence_after_seconds` | float | ❌ No | 1.5 | Silence gap duration (0-10s) for RTP segmentation |

**Response (200 OK):**
```json
{
  "call_id": "a1b2c3d4-1234-5678-abcd-0123456789ab",
  "status": "playing_audio",
  "audio_file": "menu_options.wav",
  "log_file": "logs/calls/call_20251224_103000_1234_at_sip.example.com_a1b2c3d4.log",
  "message": "Audio injection started successfully"
}
```

---

#### `GET /call/status`

Get the current call status.

**Response (200 OK):**
```json
{
  "status": "active",
  "destination": "sip:1234@sip.example.com",
  "started_at": "2025-12-24T10:30:00.123Z",
  "duration": 45,
  "duration_limit": 120,
  "current_audio": "greeting.wav"
}
```

**Call Status Values:**
- `initiated` - Call is being set up
- `ringing` - Ringing at destination
- `active` - Call connected and ready
- `playing_audio` - Audio currently playing
- `terminated` - Call ended normally
- `failed` - Call failed to connect

---

#### `POST /call/end`

End the active call.

**Response (200 OK):**
```json
{
  "call_id": "a1b2c3d4-1234-5678-abcd-0123456789ab",
  "status": "terminated",
  "duration": 78,
  "log_file": "logs/calls/call_20251224_103000_1234_at_sip.example.com_a1b2c3d4.log",
  "message": "Call ended successfully"
}
```

---

## 🎵 Audio File Management

### Audio File Requirements

- ✅ **Format:** WAV (PCM)
- ✅ **Sample Rate:** 8-48kHz (8kHz recommended for SIP)
- ✅ **Channels:** Mono or Stereo
- ✅ **Bit Depth:** 16-bit recommended

### Adding Audio Files

Place your WAV files in the `assets/audio/` directory:

```bash
# Local development
cp your_audio.wav assets/audio/

# Remote server
scp your_audio.wav user@server:/opt/linphone-caller/assets/audio/
```

### Converting Audio Files

```bash
# Convert MP3 to WAV (8kHz, mono, 16-bit)
ffmpeg -i input.mp3 -ar 8000 -ac 1 -sample_fmt s16 output.wav

# Convert any format to SIP-optimized WAV
ffmpeg -i input.* -ar 8000 -ac 1 -ab 128k -f wav output.wav
```

---

## 🔧 Configuration

### SIP Configuration

Edit `config/linphonerc`:

```ini
[sip]
sip_port=5060
sip_tcp_port=5060
sip_tls_port=5061
guess_hostname=1
inc_timeout=30
in_call_timeout=0
delayed_timeout=4
use_info=0
register_only_when_network_is_up=1
register_only_when_upnp_is_ok=1

[sound]
echocancellation=0
playback_dev_id=ALSA: default
capture_dev_id=ALSA: default

[video]
enabled=0
```

### Environment Variables

Create a `.env` file:

```env
# Application
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

# Linphone
LINPHONE_BINARY=/usr/bin/linphonec
LINPHONE_CONFIG=/opt/linphone-caller/config/linphonerc

# Paths
AUDIO_DIRECTORY=/opt/linphone-caller/assets/audio
LOG_DIRECTORY=/opt/linphone-caller/logs
```

---

## 🐳 Docker Deployment

### Using Docker

```bash
# Build image
docker build -t linphone-sip-audio-injector .

# Run container
docker run -d \
  --name linphone-audio-api \
  -p 8000:8000 \
  -v $(pwd)/assets/audio:/app/assets/audio \
  -v $(pwd)/logs:/app/logs \
  linphone-sip-audio-injector
```

### Docker Compose

```yaml
version: '3.8'

services:
  linphone-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./assets/audio:/app/assets/audio
      - ./logs:/app/logs
    environment:
      - APP_HOST=0.0.0.0
      - APP_PORT=8000
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

---

## 🖥️ Production Deployment

### Systemd Service

1. **Deploy using the included script:**

```bash
./scripts/deploy.sh
```

2. **Or manually install the systemd service:**

```bash
# Copy service file
sudo cp systemd/linphone-caller.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable linphone-caller
sudo systemctl start linphone-caller

# Check status
sudo systemctl status linphone-caller
```

### Monitoring Logs

```bash
# Application logs
tail -f logs/app.log

# Per-call logs
tail -f logs/calls/call_*.log

# System service logs
sudo journalctl -u linphone-caller -f
```

---

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Integration Testing Script

```bash
# Test full call flow
./scripts/test_call_flow.sh

# Test multiple audio injections
./scripts/test_audio_injection.sh
```

### Manual Testing

```bash
# Start a test call
curl -X POST http://localhost:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{"destination": "sip:echo@sip2sip.info", "duration": 60}'

# Inject test audio
curl -X POST http://localhost:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{"audio_file": "test_audio.wav"}'
```

---

## 🔍 Troubleshooting

### Issue: "No active call to inject audio into"

**Cause:** Call hasn't started or already ended.

**Solution:**
```bash
# Check call status first
curl http://localhost:8000/api/v1/call/status
```

---

### Issue: "Audio file not found"

**Cause:** WAV file doesn't exist in `assets/audio/`.

**Solution:**
```bash
# List available audio files
ls -lh assets/audio/

# Add your audio file
cp your_audio.wav assets/audio/
```

---

### Issue: "linphonec not found"

**Cause:** Linphone CLI not installed.

**Solution:**
```bash
# Install linphone-cli
sudo apt update
sudo apt install -y linphone-cli

# Verify installation
which linphonec
linphonec --version
```

---

### Issue: "Address already in use" (Port 5060)

**Cause:** Another linphonec process is running.

**Solution:**
```bash
# Kill existing processes
pkill -9 linphonec

# Restart the service
sudo systemctl restart linphone-caller
```

---

### Issue: Audio not playing or cutting off

**Cause:** Audio duration calculation or silence gap configuration.

**Solution:**
- Check audio file format (must be valid WAV)
- Verify audio is not longer than call duration
- Check logs for audio completion messages
- Adjust `silence_after_seconds` if needed

---

## 📚 Advanced Topics

### RTP Stream Segmentation for Transcription

The `silence_after_seconds` parameter is crucial for speech-to-text transcription systems:

**Without silence gap:**
```
Transcript: "Do you have ICU facilities? How do I book an appointment?"
(Multiple questions merged)
```

**With silence gap (1.5s):**
```
Transcript Line 1: "Do you have ICU facilities?"
Transcript Line 2: "How do I book an appointment?"
(Properly segmented)
```

The silence gap creates a break in the RTP stream, allowing transcription systems to detect utterance boundaries.

---

### Audio Interruption Behavior

When a new `/playAudio` request is made while audio is playing:

1. **Current audio is interrupted** immediately
2. **New audio starts** right away
3. **Background task is cancelled** gracefully
4. **No audio queueing** - only the most recent audio plays

This is perfect for dynamic IVR systems where user input should interrupt prompts.

---

### Custom Audio Processing Pipeline

```python
# Example: Process user input and respond dynamically
import requests
from speech_recognition import recognize_speech

API_BASE = "http://localhost:8000/api/v1"

def handle_ivr_flow():
    # Start call
    requests.post(f"{API_BASE}/call/start", json={
        "destination": "sip:customer@example.com",
        "duration": 300,
        "audio_file": "main_menu.wav"
    })
    
    # Listen for user response (pseudo-code)
    user_input = recognize_speech()
    
    # Play appropriate response (interrupts main menu if still playing)
    if user_input == "billing":
        requests.post(f"{API_BASE}/call/playAudio", json={
            "audio_file": "billing_menu.wav"
        })
    elif user_input == "support":
        requests.post(f"{API_BASE}/call/playAudio", json={
            "audio_file": "support_menu.wav"
        })
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone repository
git clone https://github.com/rathnavel/linphone-sip-audio-injector.git
cd linphone-sip-audio-injector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Format code
black app/
isort app/

# Lint
flake8 app/
```

### Guidelines

- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Keep commit messages clear and descriptive

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Linphone** - Open-source SIP client
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server implementation

---

## 📞 Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/rathnavel/linphone-sip-audio-injector/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/rathnavel/linphone-sip-audio-injector/discussions)
- 📧 **Contact:** Open an issue for questions

---

## 🗺️ Roadmap

- [ ] WebSocket support for real-time events
- [ ] Multiple concurrent calls
- [ ] Audio format auto-conversion
- [ ] Call recording capabilities
- [ ] Prometheus metrics export
- [ ] Kubernetes deployment manifests
- [ ] Web-based admin panel

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ by Rathnavel**

*Built for the SIP/VoIP community*

