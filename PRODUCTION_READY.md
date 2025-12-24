# 📞 Linphone Caller - Production Ready Documentation

**Status:** ✅ **PRODUCTION READY**  
**Version:** 2.0  
**Last Updated:** December 22, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Deployment](#deployment)
6. [Scripts Reference](#scripts-reference)
7. [Configuration](#configuration)
8. [Usage Examples](#usage-examples)
9. [Logging](#logging)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Linphone Caller is a production-ready HTTP API service that enables programmatic SIP call management with real-time audio injection capabilities. Built with FastAPI and linphonec, it provides a reliable interface for automated voice applications.

### Key Capabilities

- **Direct SIP Calls**: No SIP provider account needed - make direct calls to any SIP URI
- **Single Call Focus**: One active call at a time for simplicity and reliability
- **Audio Injection**: Play unlimited WAV files during active calls
- **Auto-Play Audio**: Automatically play audio when call is answered (with configurable delay)
- **Per-Call Logging**: Detailed logs for every call session with unique IDs
- **REST API**: Clean HTTP endpoints for all operations
- **Production Grade**: Systemd service with auto-restart and boot startup

---

## ✅ Features

### Call Management
- ✅ **Start Calls**: Initiate outbound SIP calls with configurable duration
- ✅ **Auto-Play Audio**: Optionally play audio automatically when call is answered
- ✅ **Status Monitoring**: Real-time call status (initiated → ringing → active → terminated)
- ✅ **Manual Termination**: End calls via API before duration limit
- ✅ **Auto Termination**: Calls end automatically at duration limit
- ✅ **Remote Hangup Detection**: Detects when remote party ends the call

### Audio Features
- ✅ **Multiple Injections**: Inject unlimited audio files in a single call (tested with 6+ files)
- ✅ **RTP Stream Segmentation**: Configurable silence gaps between audio for proper transcription segmentation
- ✅ **Auto-Play on Answer**: Configure audio to play automatically with delay after answer
- ✅ **WAV Format Support**: Supports various WAV formats (8-48kHz, mono/stereo)
- ✅ **Background Noise Suppression**: Automatically stops comfort noise
- ✅ **Sequential Playback**: Queue multiple audio files
- ✅ **No Crashes**: Stable audio injection without process crashes

### Logging & Monitoring
- ✅ **Per-Call Logs**: Unique log file for each call with UUID
- ✅ **Detailed Events**: All linphone stdout/stderr captured
- ✅ **Application Logs**: Centralized logging with call prefixes
- ✅ **Call Summary**: Duration, status, and stats at call end
- ✅ **Health Checks**: API endpoint for service health monitoring

### Deployment & Operations
- ✅ **Systemd Service**: Auto-start on boot, auto-restart on failure
- ✅ **Easy Deployment**: Single-script deployment process
- ✅ **Quick Updates**: Fast code update and restart script
- ✅ **Configuration Management**: Centralized config with sensible defaults
- ✅ **Python Virtual Environment**: Isolated dependencies

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP API Layer (FastAPI)                 │
│  ┌───────────┬──────────────┬──────────────┬──────────────┐ │
│  │  /start   │ /playAudio   │   /status    │    /end      │ │
│  └───────────┴──────────────┴──────────────┴──────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              LinphoneController (Business Logic)            │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ - Call State Management                                  ││
│  │ - Process Lifecycle Control                              ││
│  │ - Audio Injection Logic                                  ││
│  │ - Auto-Play Scheduling                                   ││
│  │ - Output Parsing & Status Detection                      ││
│  └─────────────────────────────────────────────────────────┘│
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              linphonec Process (SIP Client)                 │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Command:  linphonec -c /path/to/linphonerc              ││
│  │                                                          ││
│  │ stdin  →  soundcard use files                            ││
│  │       →  play /dev/zero     (stop background audio)      ││
│  │       →  call sip:user@host:port                         ││
│  │       →  play /path/to/audio.wav (inject audio)          ││
│  │       →  terminate                                       ││
│  │       →  quit                                            ││
│  │                                                          ││
│  │ stdout →  Call status updates (ringing, connected...)    ││
│  │ stderr →  Debug messages & errors                        ││
│  └─────────────────────────────────────────────────────────┘│
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   SIP Network  │
                    │ (Direct Calls) │
                    └────────────────┘
```

### Call Flow

```
1. API Request
   POST /api/v1/call/start
   {
     "destination": "sip:1001@192.168.1.40:5060",
     "duration": 120,
     "audio_file": "greeting.wav",      // Optional
     "play_after_seconds": 2             // Optional
   }
   ▼
2. Start linphonec Process
   - Launch: linphonec -c /path/to/config
   - Send: soundcard use files
   - Send: play /dev/zero (stop background noise)
   - Send: call sip:1001@192.168.1.40:5060
   ▼
3. Monitor Output Streams
   - Parse stdout for status: ringing → connected → established
   - Capture stderr for debug messages
   - Update call status in real-time
   ▼
4. Call Answered (Status: ACTIVE)
   - Media streams established
   - If auto_play_audio configured:
     → Wait play_after_seconds
     → Inject audio automatically
   ▼
5. Audio Injection (Manual or Auto)
   - Send: play /path/to/audio.wav
   - Can inject unlimited times
   - No process crashes
   ▼
6. Call Termination
   - Duration limit reached, OR
   - Manual termination via API, OR
   - Remote party hangs up
   - Send: terminate
   - Send: quit
   - Cleanup process
   ▼
7. Logging & Cleanup
   - Write call summary to per-call log
   - Clear current_call object
   - Ready for next call
```

### File Structure

```
/opt/linphone-caller/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # API endpoint definitions
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Centralized configuration
│   │   ├── linphone_controller.py # Core call management logic
│   │   └── call_logger.py         # Per-call logging
│   └── models/
│       ├── __init__.py
│       └── schemas.py             # Pydantic request/response models
├── assets/
│   └── audio/                     # WAV audio files for injection
│       ├── greeting.wav
│       ├── menu_options.wav
│       └── ...
├── config/
│   └── linphonerc                 # Linphone SIP client configuration
├── scripts/
│   ├── install.sh                 # Initial installation script
│   ├── deploy.sh                  # Deploy as systemd service
│   ├── update.sh                  # Quick update after code changes
│   ├── start.sh                   # Manual start (dev mode)
│   ├── stop.sh                    # Manual stop
│   └── logs.sh                    # View logs
├── logs/
│   ├── app.log                    # Main application log
│   └── calls/                     # Per-call detailed logs
│       ├── call_20251222_103045_1001_at_192.168.1.40_5060_abc12345.log
│       └── ...
├── venv/                          # Python virtual environment
├── requirements.txt               # Python dependencies
└── deploy-changes.sh              # Local machine deploy script (optional)
```

---

## 📡 API Reference

**Base URL:** `http://<vm-ip>:8000/api/v1`

### 1. Health Check

Check if the service is running and linphone is available.

**Endpoint:** `GET /health`

**Request:**
```bash
curl http://192.168.1.80:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "linphone_available": true,
  "timestamp": "2025-12-22T10:30:00.000Z",
  "audio_directory_accessible": true,
  "has_active_call": false
}
```

---

### 2. Start Call

Initiate a new outbound SIP call. Only ONE call can be active at a time.

**Endpoint:** `POST /call/start`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "destination": "sip:1001@192.168.1.40:5060",
  "duration": 120,
  "audio_file": "greeting.wav",
  "play_after_seconds": 2
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `destination` | string | ✅ Yes | - | SIP URI (must start with `sip:`) |
| `duration` | integer | ❌ No | 120 | Call duration in seconds (1-900, 15 minutes max) |
| `audio_file` | string | ❌ No | null | Audio file to auto-play when answered |
| `play_after_seconds` | integer | ❌ No | 0 | Delay in seconds before auto-play (0-60) |

**Example Request:**
```bash
# Basic call (no auto-play)
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1001@192.168.1.40:5060",
    "duration": 120
  }'

# Call with auto-play (plays immediately after answer)
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1001@192.168.1.40:5060",
    "duration": 180,
    "audio_file": "greeting.wav",
    "play_after_seconds": 0
  }'

# Call with delayed auto-play (waits 5 seconds after answer)
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1001@192.168.1.40:5060",
    "duration": 180,
    "audio_file": "welcome_message.wav",
    "play_after_seconds": 5
  }'
```

**Response (Success - 200):**
```json
{
  "status": "ringing",
  "call_id": "a1b2c3d4-1234-5678-abcd-0123456789ab",
  "destination": "sip:1001@192.168.1.40:5060",
  "started_at": "2025-12-22T10:30:15.123456",
  "duration_limit": 120,
  "log_file": "logs/calls/call_20251222_103015_1001_at_192.168.1.40_5060_a1b2c3d4.log",
  "message": "Call initiated successfully"
}
```

**Response (Error - 409 Conflict):**
```json
{
  "detail": "A call is already in progress to sip:1002@192.168.1.40:5060. End the current call before starting a new one."
}
```

**Response (Error - 404 Not Found):**
```json
{
  "detail": "Audio file not found: nonexistent.wav"
}
```

---

### 3. Get Call Status

Check the status of the active call.

**Endpoint:** `GET /call/status`

**Request:**
```bash
curl http://192.168.1.80:8000/api/v1/call/status
```

**Response (Call Active - 200):**
```json
{
  "status": "active",
  "destination": "sip:1001@192.168.1.40:5060",
  "started_at": "2025-12-22T10:30:15.123456",
  "duration": 35,
  "duration_limit": 120,
  "current_audio": "greeting.wav"
}
```

**Call Status Values:**
- `initiated` - Call is being initiated
- `ringing` - Destination is ringing
- `active` - Call is connected and active
- `playing_audio` - Currently injecting audio
- `terminated` - Call has ended
- `failed` - Call failed to connect

**Response (No Active Call - 404):**
```json
{
  "detail": "No active call"
}
```

---

### 4. Inject Audio

Play an audio file into the active call. Can be called multiple times.

**⚡ Non-Blocking**: This endpoint returns immediately after starting audio playback. The audio and silence gap play in the background.

**⏭️ Interruption Behavior**: If audio is currently playing when a new `/playAudio` request is made, the current audio will be **interrupted** and the new audio will start immediately. This ensures the most recent audio request always plays without delay.

**Endpoint:** `POST /call/playAudio`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "audio_file": "menu_options.wav",
  "silence_after_seconds": 1.5
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `audio_file` | string | ✅ Yes | Name of WAV file in `assets/audio/` directory |
| `silence_after_seconds` | float | ❌ No | Silence duration after audio (default: 1.5s). Creates RTP stream gap for transcription segmentation. Range: 0-10 seconds. |

**Audio File Requirements:**
- ✅ Must be `.wav` format
- ✅ Must exist in `assets/audio/` directory
- ✅ No path separators allowed (`/`, `\`, `..`)
- ✅ Supports 8-48kHz, mono or stereo

**RTP Stream Segmentation for Transcription:**

The `silence_after_seconds` parameter is crucial for transcription systems. Without it, back-to-back audio injections create a continuous RTP stream, causing transcription systems to treat multiple audio files as one continuous utterance.

**Problem Without Silence Gap:**
```
Customer: Do you have ICU facilities? How do I book an appointment? Do you have a pharmacy?
```
(All 3 questions merged into one line)

**Solution With Silence Gap (default 1.5s):**
```
Customer: Do you have ICU facilities?
Customer: How do I book an appointment?
Customer: Do you have a pharmacy?
```
(Each question properly separated)

**Example Request (Basic):**
```bash
curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{
    "audio_file": "menu_options.wav"
  }'
```

**Example Request (Custom Silence):**
```bash
curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{
    "audio_file": "menu_options.wav",
    "silence_after_seconds": 2.0
  }'
```

**Example Request (No Silence Gap):**
```bash
# Use this only if you want continuous audio without breaks
curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{
    "audio_file": "menu_options.wav",
    "silence_after_seconds": 0
  }'
```

**Response (Success - 200):**
```json
{
  "call_id": "a1b2c3d4-1234-5678-abcd-0123456789ab",
  "status": "active",
  "audio_file": "menu_options.wav",
  "log_file": "logs/calls/call_20251222_103015_1001_at_192.168.1.40_5060_a1b2c3d4.log",
  "message": "Audio injection started successfully"
}
```

**Response (Error - 404 Not Found):**
```json
{
  "detail": "No active call to inject audio into"
}
```

```json
{
  "detail": "Audio file not found: nonexistent.wav"
}
```

**⏱️ Timing & Sequencing:**

The `/playAudio` endpoint is **non-blocking** and returns immediately (~100ms). The actual audio playback and silence gap happen in the background.

**Single Audio Timeline:**
```
0.0s  → API call returns with 200 OK ✅
0.0s  → Audio starts playing in background (e.g., 4.5s duration)
4.5s  → Audio completes
4.7s  → Silence gap starts (1.5s by default)
6.2s  → Silence completes, status → ACTIVE
```

**Multiple Rapid Calls (Interruption Behavior):**

If you make multiple `/playAudio` calls rapidly, **the newest audio always interrupts and replaces the current audio**:

```bash
# All 3 calls return immediately (within 300ms total)
curl POST /playAudio -d '{"audio_file":"audio1.wav"}'  # Returns ~0.1s
sleep 0.5
curl POST /playAudio -d '{"audio_file":"audio2.wav"}'  # Returns ~0.1s  
sleep 0.5
curl POST /playAudio -d '{"audio_file":"audio3.wav"}'  # Returns ~0.1s

# What actually plays:
# 0.0s   → audio1 starts
# 0.5s   → audio1 INTERRUPTED by audio2
# 0.5s   → audio2 starts
# 1.0s   → audio2 INTERRUPTED by audio3
# 1.0s   → audio3 starts
# 5.5s   → audio3 completes
# 5.7s   → silence gap
# 7.2s   → all complete

# Result: Only audio3 plays completely
```

**Usage Patterns:**

```bash
# Pattern 1: Single Audio Play (MOST COMMON)
curl POST /playAudio -d '{"audio_file":"greeting.wav"}'
# Returns immediately, audio plays to completion

# Pattern 2: Sequential Audio with Gaps
curl POST /playAudio -d '{"audio_file":"question1.wav"}'
sleep 8  # Wait for audio + silence to complete
curl POST /playAudio -d '{"audio_file":"question2.wav"}'
sleep 8
curl POST /playAudio -d '{"audio_file":"question3.wav"}'
# Each plays to completion before next starts

# Pattern 3: Dynamic Audio Replacement (Advanced)
curl POST /playAudio -d '{"audio_file":"long_menu.wav"}'
# User presses button 30 seconds later
curl POST /playAudio -d '{"audio_file":"option_selected.wav"}'
# Immediately interrupts long_menu and plays option_selected
```

**✅ Advantages:**
- **Fast API responses** - Never wait for audio to finish
- **Immediate interruption** - Most recent audio always plays
- **Responsive** - Perfect for dynamic IVR interactions
- **Simple** - No queue management needed

**⚠️ Important Notes:**
- All `/playAudio` calls return immediately (~100ms response time)
- **New audio interrupts current audio** - Only the last audio plays completely
- If you need sequential playback, add delays between API calls (audio_duration + silence_gap)
- Check call logs to see actual playback start/interruption times
- Ending a call cancels any ongoing audio playback

---

### 5. End Call

Terminate the active call before its duration limit.

**Endpoint:** `POST /call/end`

**Request:**
```bash
curl -X POST http://192.168.1.80:8000/api/v1/call/end
```

**Response (Success - 200):**
```json
{
  "call_id": "a1b2c3d4-1234-5678-abcd-0123456789ab",
  "status": "terminated",
  "duration": 45,
  "log_file": "logs/calls/call_20251222_103015_1001_at_192.168.1.40_5060_a1b2c3d4.log",
  "message": "Call ended successfully"
}
```

**Response (Error - 404 Not Found):**
```json
{
  "detail": "No active call to end"
}
```

---

## 🚀 Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- linphone-cli package
- Network access to SIP destination

### Initial Installation

**On the VM:**

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv linphone-cli build-essential

# 2. Create application directory
sudo mkdir -p /opt/linphone-caller
sudo chown $USER:$USER /opt/linphone-caller

# 3. Transfer files from local machine to your VM (/opt/linphone-caller/)
# (From your local machine)
cd /Users/ratbalas/Documents/Projects/cce/finesse-gadgets
rsync -avz linphone-caller/ administrator@192.168.1.80:/opt/linphone-caller/

# 4. Run installation script (on VM)
cd /opt/linphone-caller
chmod +x scripts/*.sh
./scripts/install.sh

# 5. Deploy as systemd service
sudo ./scripts/deploy.sh
```

### Service Status

```bash
# Check service status
sudo systemctl status linphone-caller

# View real-time logs
sudo journalctl -u linphone-caller -f

# Restart service
sudo systemctl restart linphone-caller

# Stop service
sudo systemctl stop linphone-caller

# Start service
sudo systemctl start linphone-caller

# Disable auto-start on boot
sudo systemctl disable linphone-caller

# Enable auto-start on boot
sudo systemctl enable linphone-caller
```

---

## 📜 Scripts Reference

### 1. `install.sh` - Initial Installation

**Purpose:** Install Python dependencies and set up the application environment.

**Location:** `/opt/linphone-caller/scripts/install.sh`

**What it does:**
1. ✅ Checks for required system packages (python3, linphone-cli)
2. ✅ Stops existing service (if running)
3. ✅ Removes old virtual environment
4. ✅ Creates fresh Python virtual environment
5. ✅ Installs dependencies from `requirements.txt`
6. ✅ Creates necessary directories (logs, assets/audio)
7. ✅ Validates configuration files
8. ✅ Creates `.env.example` if missing

**Usage:**
```bash
cd /opt/linphone-caller
./scripts/install.sh
```

**Output Example:**
```
======================================
Linphone Caller - Installation Script
======================================

[1/7] Checking for linphone-cli...
✓ linphonecsh found at: /usr/bin/linphonecsh

[2/7] Checking Python version...
✓ Python 3.10 found

[3/7] Creating virtual environment...
✓ Virtual environment created

[4/7] Installing Python dependencies...
✓ Dependencies installed

[5/7] Creating required directories...
✓ Directories created

[6/7] Validating configuration...
✓ Configuration valid

[7/7] Installation complete!
```

**When to run:**
- First time deployment
- After adding new Python dependencies
- After major updates
- When dependencies are corrupted

---

### 2. `deploy.sh` - Deploy as Systemd Service

**Purpose:** Install and enable the application as a systemd service for automatic startup and restart.

**Location:** `/opt/linphone-caller/scripts/deploy.sh`

**What it does:**
1. ✅ Creates systemd service file at `/etc/systemd/system/linphone-caller.service`
2. ✅ Configures service with proper user, working directory, and environment
3. ✅ Enables service for auto-start on boot
4. ✅ Starts the service immediately
5. ✅ Shows service status

**Systemd Service Configuration:**
```ini
[Unit]
Description=Linphone Caller HTTP API
After=network.target

[Service]
Type=simple
User=administrator
WorkingDirectory=/opt/linphone-caller
Environment="PATH=/opt/linphone-caller/venv/bin:/usr/bin"
Environment="LINPHONERC=/opt/linphone-caller/config/linphonerc"
ExecStart=/opt/linphone-caller/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Usage:**
```bash
cd /opt/linphone-caller
sudo ./scripts/deploy.sh
```

**Output Example:**
```
======================================
Deploying Linphone Caller Service
======================================

✓ Service file created
✓ Service enabled
✓ Service started

Service Status:
● linphone-caller.service - Linphone Caller HTTP API
   Loaded: loaded
   Active: active (running)
```

**When to run:**
- First time deployment
- After changing service configuration
- After moving application to new location

---

### 3. `update.sh` - Quick Update After Code Changes

**Purpose:** Clear Python cache and restart service after code changes. Run this ON THE VM.

**Location:** `/opt/linphone-caller/scripts/update.sh`

**What it does:**
1. ✅ Clears all Python cache (`__pycache__`, `*.pyc` files)
2. ✅ Restarts the systemd service
3. ✅ Checks service status and shows logs if failed

**Usage:**
```bash
# After rsync from local machine
ssh administrator@192.168.1.80

# Run update script
/opt/linphone-caller/scripts/update.sh
```

**Output Example:**
```
=====================================
  Linphone Caller - Update
=====================================

[1/3] Clearing Python cache...
✓ Cache cleared

[2/3] Restarting linphone-caller service...
✓ Service restarted

[3/3] Checking service status...
✓ Service is running

Service Status:
● linphone-caller.service - Linphone Caller HTTP API
   Active: active (running)

=====================================
  ✅ Update Complete!
=====================================

Health Check: curl http://localhost:8000/api/v1/health
```

**When to run:**
- After any Python code changes
- After updating configuration files
- When service is misbehaving (cache issues)

---

### 4. `start.sh` - Manual Start (Development Mode)

**Purpose:** Start the application manually without systemd (useful for development/testing).

**Location:** `/opt/linphone-caller/scripts/start.sh`

**What it does:**
1. ✅ Activates Python virtual environment
2. ✅ Sets LINPHONERC environment variable
3. ✅ Starts FastAPI with Uvicorn
4. ✅ Runs in foreground with logs

**Usage:**
```bash
cd /opt/linphone-caller
./scripts/start.sh
```

**Output Example:**
```
Starting Linphone Caller API...
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**When to run:**
- Development and testing
- Debugging issues
- When you want to see logs in real-time in terminal
- Testing before systemd deployment

**Stop:** Press `Ctrl+C`

---

### 5. `stop.sh` - Stop Service

**Purpose:** Stop the running linphone-caller service.

**Location:** `/opt/linphone-caller/scripts/stop.sh`

**What it does:**
1. ✅ Stops the systemd service

**Usage:**
```bash
cd /opt/linphone-caller
sudo ./scripts/stop.sh
```

**When to run:**
- Before maintenance
- Before major updates
- When troubleshooting

---

### 6. `logs.sh` - View Application Logs

**Purpose:** Quickly view application logs (main log and recent call logs).

**Location:** `/opt/linphone-caller/scripts/logs.sh`

**What it does:**
1. ✅ Shows last 50 lines of main application log
2. ✅ Lists recent call logs

**Usage:**
```bash
cd /opt/linphone-caller
./scripts/logs.sh

# Or view specific call log
tail -f logs/calls/call_20251222_*.log
```

**When to run:**
- Debugging issues
- Reviewing call history
- Checking application health

---

### 7. `deploy-changes.sh` - Deploy from Local Machine (Optional)

**Purpose:** One-command deployment from your local machine. Syncs files and restarts service.

**Location:** `/Users/ratbalas/Documents/Projects/cce/finesse-gadgets/linphone-caller/deploy-changes.sh`

**What it does:**
1. ✅ Syncs files from local to VM (excludes venv, cache, logs)
2. ✅ Clears Python cache on VM
3. ✅ Restarts service on VM
4. ✅ Shows service status

**Usage:**
```bash
# From your local machine
/Users/ratbalas/Documents/Projects/cce/finesse-gadgets/linphone-caller/deploy-changes.sh
```

**Output Example:**
```
=====================================
  Linphone Caller - Quick Deploy
=====================================

[1/4] Syncing files to VM...
✓ Files synced successfully

[2/4] Clearing Python cache on VM...
✓ Cache cleared

[3/4] Restarting linphone-caller service...
✓ Service restarted

[4/4] Checking service status...
✓ Service is running

=====================================
  ✅ Deploy Complete!
=====================================

API Endpoint: http://192.168.1.80:8000
```

**When to run:**
- After making code changes locally
- Quick deployment workflow
- When you don't want to SSH manually

---

## ⚙️ Configuration

### Application Configuration

**File:** `/opt/linphone-caller/app/core/config.py`

```python
class Settings(BaseSettings):
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    WORKERS: int = 1

    # Call Settings
    DEFAULT_CALL_DURATION: int = 120  # seconds
    MAX_CALL_DURATION: int = 300      # seconds
    AUDIO_DIRECTORY: str = "assets/audio"

    # Linphone Settings
    LINPHONE_CONFIG_DIR: str = "config"
    LINPHONE_BINARY: str = "/usr/bin/linphonec"

    # Optional Authentication (set via environment if needed)
    API_KEY: Optional[str] = None
```

**To modify:**
1. Edit `/opt/linphone-caller/app/core/config.py`
2. Run `/opt/linphone-caller/scripts/update.sh`

---

### Linphone Configuration

**File:** `/opt/linphone-caller/config/linphonerc`

```ini
[sip]
default_proxy=0
register_only_when_network_is_up=1
verify_server_certs=1
media_encryption=none

[rtp]
audio_rtp_port=7078
video_rtp_port=9078

[sound]
echocancellation=0
playback_dev_id=ALSA: default device
capture_dev_id=ALSA: default device

[video]
enabled=0
capture=0
display=0

[net]
mtu=1300
download_bw=0
upload_bw=0
```

**Key Settings:**
- **RTP Ports**: 7078 (audio), 9078 (video, unused)
- **Echo Cancellation**: Disabled (not needed for one-way audio)
- **Video**: Completely disabled
- **Media Encryption**: None (can be changed to SRTP if needed)

**Note:** Linphone may add additional runtime settings automatically. This is normal.

---

### Audio Files

**Directory:** `/opt/linphone-caller/assets/audio/`

**Supported Formats:**
- WAV files (8kHz - 48kHz)
- Mono or Stereo
- 16-bit PCM recommended

**Adding New Audio:**
```bash
# From local machine
scp your_audio.wav administrator@192.168.1.80:/opt/linphone-caller/assets/audio/

# Verify
ssh administrator@192.168.1.80 "ls -lh /opt/linphone-caller/assets/audio/"

# Use immediately (no restart needed)
curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{"audio_file":"your_audio.wav"}'
```

---

## 💡 Usage Examples

### Example 1: Basic Call Without Audio

```bash
# Start call
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1001@192.168.1.40:5060",
    "duration": 60
  }'

# Check status
curl http://192.168.1.80:8000/api/v1/call/status

# End call
curl -X POST http://192.168.1.80:8000/api/v1/call/end
```

---

### Example 2: Call with Auto-Play Audio

```bash
# Call that plays greeting immediately when answered
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1001@192.168.1.40:5060",
    "duration": 120,
    "audio_file": "greeting.wav",
    "play_after_seconds": 0
  }'

# Call that waits 5 seconds after answer before playing
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1001@192.168.1.40:5060",
    "duration": 180,
    "audio_file": "welcome_message.wav",
    "play_after_seconds": 5
  }'
```

---

### Example 3: Call with Multiple Manual Audio Injections

```bash
# Start call
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1001@192.168.1.40:5060",
    "duration": 180
  }'

# Wait for call to connect
sleep 5

# Play first audio (with default 1.5s silence gap for transcription)
curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{"audio_file":"greeting.wav", "silence_after_seconds": 1.5}'

# Wait for audio to finish
sleep 10

# Play second audio (with 2s silence gap)
curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{"audio_file":"menu_options.wav", "silence_after_seconds": 2.0}'

# Wait
sleep 10

# Play third audio (with default silence gap)
curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{"audio_file":"closing_message.wav"}'

# End call
curl -X POST http://192.168.1.80:8000/api/v1/call/end
```

---

### Example 4: Auto-Play + Manual Injections

```bash
# Start with auto-play greeting
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1001@192.168.1.40:5060",
    "duration": 180,
    "audio_file": "greeting.wav",
    "play_after_seconds": 2
  }'

# Greeting plays automatically 2 seconds after answer

# Wait 15 seconds
sleep 15

# Inject additional audio manually
curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{"audio_file":"menu_options.wav"}'

sleep 10

# More audio
curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{"audio_file":"thank_you.wav"}'
```

---

### Example 5: Python Script for IVR Flow

```python
#!/usr/bin/env python3
import requests
import time

API_BASE = "http://192.168.1.80:8000/api/v1"

def make_ivr_call():
    """Make an IVR call with multiple prompts."""
    
    # Start call with auto-play greeting
    print("📞 Starting call...")
    response = requests.post(f"{API_BASE}/call/start", json={
        "destination": "sip:1001@192.168.1.40:5060",
        "duration": 300,
        "audio_file": "welcome.wav",
        "play_after_seconds": 1
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to start call: {response.text}")
        return
    
    call_data = response.json()
    print(f"✅ Call started: {call_data['call_id']}")
    
    # Wait for greeting to finish
    time.sleep(12)
    
    # Play menu options
    prompts = [
        ("main_menu.wav", 15),
        ("press_1_for_appointments.wav", 8),
        ("press_2_for_billing.wav", 8),
        ("press_3_for_pharmacy.wav", 8),
        ("closing_message.wav", 10)
    ]
    
    for audio_file, wait_time in prompts:
        print(f"🎵 Playing: {audio_file}")
        response = requests.post(f"{API_BASE}/call/playAudio", json={
            "audio_file": audio_file,
            "silence_after_seconds": 1.5  # Add silence gap for transcription segmentation
        })
        
        if response.status_code == 200:
            print(f"✅ Audio injected: {audio_file}")
        else:
            print(f"❌ Failed to inject audio: {response.text}")
        
        time.sleep(wait_time)
    
    # Check final status
    response = requests.get(f"{API_BASE}/call/status")
    if response.status_code == 200:
        status = response.json()
        print(f"📊 Call duration: {status['duration']}s")
    
    # End call
    print("🛑 Ending call...")
    response = requests.post(f"{API_BASE}/call/end")
    
    if response.status_code == 200:
        end_data = response.json()
        print(f"✅ Call ended: Duration {end_data['duration']}s")
        print(f"📋 Log file: {end_data['log_file']}")

if __name__ == "__main__":
    make_ivr_call()
```

**Run:**
```bash
chmod +x ivr_call.py
python3 ivr_call.py
```

---

### Example 6: Bash Script for Sequential Calls

```bash
#!/bin/bash

API_BASE="http://192.168.1.80:8000/api/v1"

# List of numbers to call
NUMBERS=(
    "sip:1001@192.168.1.40:5060"
    "sip:1002@192.168.1.40:5060"
    "sip:1003@192.168.1.40:5060"
)

# Call each number with a message
for number in "${NUMBERS[@]}"; do
    echo "📞 Calling $number..."
    
    # Start call with auto-play
    curl -s -X POST "$API_BASE/call/start" \
      -H 'Content-Type: application/json' \
      -d "{
        \"destination\": \"$number\",
        \"duration\": 60,
        \"audio_file\": \"notification_message.wav\",
        \"play_after_seconds\": 2
      }" | jq '.'
    
    # Wait for call to complete
    sleep 65
    
    echo "✅ Call to $number completed"
    echo "---"
done

echo "🎉 All calls completed!"
```

---

## 📊 Logging

### Application Log

**Location:** `/opt/linphone-caller/logs/app.log`

**Format:**
```
2025-12-22 10:30:15 | INFO | app.core.call_logger:log - [Call a1b2c3d4] Call initialized | destination=sip:1001@... | duration_limit=120
2025-12-22 10:30:15 | INFO | app.core.call_logger:log - [Call a1b2c3d4] 📞 Starting linphonec: /usr/bin/linphonec -c /opt/...
2025-12-22 10:30:17 | INFO | app.core.call_logger:log - [Call a1b2c3d4] 📡 Enabling file mode for audio playback
2025-12-22 10:30:17 | INFO | app.core.call_logger:log - [Call a1b2c3d4] 🔇 Stopping background audio
2025-12-22 10:30:18 | INFO | app.core.call_logger:log - [Call a1b2c3d4] 📞 Sending call command: call sip:1001@...
2025-12-22 10:30:18 | INFO | app.core.call_logger:log - [Call a1b2c3d4] 🔔 Call ringing
2025-12-22 10:30:20 | INFO | app.core.call_logger:log - [Call a1b2c3d4] ✓ Call connected
2025-12-22 10:30:20 | INFO | app.core.call_logger:log - [Call a1b2c3d4] ✓ Media streams established
2025-12-22 10:30:22 | INFO | app.core.call_logger:log - [Call a1b2c3d4] ⏱️  Waiting 2s before auto-playing: greeting.wav
2025-12-22 10:30:24 | INFO | app.core.call_logger:log - [Call a1b2c3d4] 🎵 Auto-playing audio: greeting.wav
```

**View:**
```bash
# Last 50 lines
tail -50 /opt/linphone-caller/logs/app.log

# Real-time
tail -f /opt/linphone-caller/logs/app.log

# With grep
tail -100 /opt/linphone-caller/logs/app.log | grep "Call a1b2c3d4"
```

---

### Per-Call Logs

**Location:** `/opt/linphone-caller/logs/calls/`

**Naming:** `call_TIMESTAMP_DESTINATION_CALLID.log`

**Example:** `call_20251222_103015_1001_at_192.168.1.40_5060_a1b2c3d4.log`

**Format:**
```
================================================================================
LINPHONE CALL LOG
================================================================================
Call ID:      a1b2c3d4-1234-5678-abcd-0123456789ab
Destination:  sip:1001@192.168.1.40:5060
Started:      2025-12-22 10:30:15.123
================================================================================

[2025-12-22 10:30:15.124] [INFO    ] Call initialized | destination=sip:1001@... | duration_limit=120 | auto_play_audio=greeting.wav | play_after_seconds=2
[2025-12-22 10:30:15.125] [INFO    ] Starting call | destination=sip:1001@... | duration_limit=120
[2025-12-22 10:30:15.126] [INFO    ] 📞 Starting linphonec: /usr/bin/linphonec -c /opt/...
[2025-12-22 10:30:17.200] [ERROR   ] [Linphone Error] 2025-12-22 10:30:17:200 belle-sip-error-TCP bind() failed...
[2025-12-22 10:30:17.500] [INFO    ] 📡 Enabling file mode for audio playback
[2025-12-22 10:30:17.510] [INFO    ] [Linphone] linphonec> Using wav files instead of soundcard.
[2025-12-22 10:30:17.800] [INFO    ] 🔇 Stopping background audio
[2025-12-22 10:30:18.100] [INFO    ] 📞 Sending call command: call sip:1001@...
[2025-12-22 10:30:18.150] [INFO    ] [Linphone] Call 1 to sip:1001@... in progress.
[2025-12-22 10:30:18.151] [INFO    ] 📞 Detected linphone call ID: 1
[2025-12-22 10:30:18.152] [INFO    ] State changed: initiated → ringing
[2025-12-22 10:30:18.153] [INFO    ] 🔔 Call ringing
[2025-12-22 10:30:20.500] [INFO    ] [Linphone] Call 1 with sip:1001@... connected.
[2025-12-22 10:30:20.501] [INFO    ] ✓ Call connected
[2025-12-22 10:30:20.502] [INFO    ] State changed: ringing → active
[2025-12-22 10:30:20.520] [INFO    ] [Linphone] Media streams established with sip:1001@... for call 1 (audio).
[2025-12-22 10:30:20.521] [INFO    ] ✓ Media streams established
[2025-12-22 10:30:22.000] [INFO    ] ⏱️  Waiting 2s before auto-playing: greeting.wav
[2025-12-22 10:30:24.001] [INFO    ] 🎵 Auto-playing audio: greeting.wav
[2025-12-22 10:30:24.002] [INFO    ] Injecting audio: greeting.wav
[2025-12-22 10:30:24.003] [INFO    ] State changed: active → playing_audio
[2025-12-22 10:30:24.004] [INFO    ] 🎵 Sending play command: play /opt/linphone-caller/assets/audio/greeting.wav
[2025-12-22 10:30:24.500] [INFO    ] State changed: playing_audio → active
...

================================================================================
CALL SUMMARY
================================================================================
Call ID:       a1b2c3d4-1234-5678-abcd-0123456789ab
Destination:   sip:1001@192.168.1.40:5060
Started:       2025-12-22 10:30:15
Ended:         2025-12-22 10:31:00
Duration:      45.23 seconds
Final Status:  terminated
================================================================================
```

**View Recent Calls:**
```bash
# List recent call logs
ls -lht /opt/linphone-caller/logs/calls/ | head -10

# View specific call
tail -100 /opt/linphone-caller/logs/calls/call_20251222_103015_*.log

# Search across all calls
grep "Audio injection" /opt/linphone-caller/logs/calls/*.log
```

---

### Systemd Journal Logs

**View:**
```bash
# Real-time logs
sudo journalctl -u linphone-caller -f

# Last 100 lines
sudo journalctl -u linphone-caller -n 100

# Today's logs
sudo journalctl -u linphone-caller --since today

# Errors only
sudo journalctl -u linphone-caller -p err

# With timestamps
sudo journalctl -u linphone-caller -n 50 --no-pager
```

---

## 🔧 Troubleshooting

### Issue: Service Won't Start

**Symptoms:**
```bash
sudo systemctl status linphone-caller
# Shows: failed (Result: exit-code)
```

**Solution:**
```bash
# Check error logs
sudo journalctl -u linphone-caller -n 50

# Common issues:
# 1. Port 8000 already in use
sudo lsof -i :8000
# Kill the process or change PORT in config.py

# 2. Virtual environment missing
cd /opt/linphone-caller
./scripts/install.sh

# 3. Permission issues
sudo chown -R administrator:administrator /opt/linphone-caller
```

---

### Issue: Audio Not Heard by Caller

**Symptoms:**
- API returns success
- Logs show audio injection
- But caller doesn't hear audio

**Solution:**
```bash
# 1. Check audio file exists
ls -lh /opt/linphone-caller/assets/audio/your_audio.wav

# 2. Check audio file format
file /opt/linphone-caller/assets/audio/your_audio.wav
# Should show: RIFF (little-endian) data, WAVE audio

# 3. Check call is active
curl http://192.168.1.80:8000/api/v1/call/status
# Status should be "active"

# 4. Check per-call log for errors
tail -50 /opt/linphone-caller/logs/calls/call_*.log | grep -i error
```

---

### Issue: "A call is already in progress"

**Symptoms:**
```json
{"detail": "A call is already in progress to sip:..."}
```

**Solution:**
```bash
# Check call status
curl http://192.168.1.80:8000/api/v1/call/status

# If call is stuck, end it
curl -X POST http://192.168.1.80:8000/api/v1/call/end

# If that doesn't work, restart service
sudo systemctl restart linphone-caller
```

---

### Issue: Call Ends with "Unknown Error"

**Symptoms:**
```
[Linphone] Call 1 with sip:... ended (Unknown error).
```

**Explanation:**
This is **NORMAL** when the remote party hangs up first. Linphone reports it as "Unknown error" but it's not an actual error.

**No action needed.**

---

### Issue: Multiple "linphonec>" in Logs

**Symptoms:**
```
[Linphone] linphonec> linphonec> linphonec> Call 1...
```

**Explanation:**
This is cosmetic. It occurs because async stdout reading accumulates prompts in the buffer.

**Impact:** None - doesn't affect functionality.

**Solution:** Already cleaned up in logs where possible. Can be ignored.

---

### Issue: Background Audio/Comfort Noise

**Symptoms:**
- Hear continuous tone or static during call
- Happens before audio injection

**Solution:**
Already fixed! The code now runs `play /dev/zero` automatically to stop background audio.

**If still happening:**
```bash
# Check per-call log to confirm command is running
tail -50 /opt/linphone-caller/logs/calls/call_*.log | grep "Stopping background audio"

# Should see:
# [INFO] 🔇 Stopping background audio
```

---

### Issue: API Returns 500 Internal Server Error

**Symptoms:**
```json
{"detail": "Internal server error"}
```

**Solution:**
```bash
# Check application logs
tail -100 /opt/linphone-caller/logs/app.log

# Check systemd logs
sudo journalctl -u linphone-caller -n 100

# Common causes:
# 1. Linphonec not installed
which linphonec
# If missing: sudo apt-get install -y linphone-cli

# 2. Config file missing
ls -lh /opt/linphone-caller/config/linphonerc

# 3. Python exception
# Check logs for traceback
```

---

### Issue: Auto-Play Audio Not Playing

**Symptoms:**
- Call starts successfully
- No audio plays automatically
- Logs don't show auto-play attempt

**Solution:**
```bash
# 1. Check request included audio_file
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:1001@192.168.1.40:5060",
    "duration": 120,
    "audio_file": "greeting.wav",      # <- Must be present
    "play_after_seconds": 2             # <- Optional
  }'

# 2. Check per-call log
tail -100 /opt/linphone-caller/logs/calls/call_*.log | grep -i "auto-play"

# Should see:
# [INFO] ⏱️  Waiting 2s before auto-playing: greeting.wav
# [INFO] 🎵 Auto-playing audio: greeting.wav

# 3. Verify audio file exists
ls -lh /opt/linphone-caller/assets/audio/greeting.wav
```

---

## 📈 Performance & Limits

### System Resources

**Typical Usage (per call):**
- CPU: <5%
- RAM: ~50MB
- Network: ~64kbps (G.711 codec)

**Scaling:**
- Current implementation: 1 call at a time
- For multiple concurrent calls: Deploy multiple instances on different ports

### Call Limits

- **Duration:** 1-300 seconds (configurable)
- **Audio Injections:** Unlimited per call
- **Audio File Size:** No hard limit (tested up to 5MB)
- **Audio File Length:** No limit (tested up to 60 seconds)

### Network Requirements

- **Bandwidth:** Minimum 128kbps per call
- **Latency:** <200ms recommended
- **Ports:** 
  - TCP 8000 (HTTP API)
  - UDP 7078 (RTP audio)
  - UDP 5060 (SIP signaling, optional)

---

## 🔒 Security Considerations

### Current Security Features

✅ **Input Validation:**
- SIP URI format validation
- Audio filename sanitization (no path traversal)
- Duration limits enforcement

✅ **Process Isolation:**
- Runs as non-root user
- Virtual environment isolation
- Systemd process management

✅ **File Access Control:**
- Audio files restricted to `assets/audio/` directory
- No arbitrary file execution

### Recommended Security Enhancements

🔐 **For Production:**

1. **Enable API Authentication:**
```python
# In config.py, set:
API_KEY: str = "your-secret-key-here"

# Then pass in requests:
curl -H "X-API-Key: your-secret-key-here" ...
```

2. **Use HTTPS:**
```bash
# Run behind nginx with SSL
# Or use uvicorn with SSL certificates
```

3. **Firewall Rules:**
```bash
# Allow only specific IPs
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

4. **Rate Limiting:**
```python
# Add to FastAPI:
from slowapi import Limiter
```

---

## 📚 Technical Details

### Why linphonec Instead of linphone-daemon?

**linphone-daemon Issues:**
- ❌ Crashes on 2nd audio injection (SIGSEGV -11)
- ❌ `incall-player-start` unstable
- ❌ Requires `--enable-lsd` for some features
- ❌ Event-based output harder to parse

**linphonec Advantages:**
- ✅ Stable for unlimited audio injections
- ✅ Simple text-based interface
- ✅ `play` command works reliably
- ✅ Human-readable output
- ✅ Well-documented commands

### Audio Injection Technical Flow

```
1. Start linphonec process with pipes (stdin/stdout/stderr)
   ↓
2. Send command: "soundcard use files\n"
   - Switches audio backend to file-based mode
   - MUST be done BEFORE call
   ↓
3. Send command: "play /dev/zero\n"
   - Plays silence to stop background comfort noise
   - Prevents unwanted audio artifacts
   ↓
4. Send command: "call sip:1001@...\n"
   - Initiates SIP call
   - linphonec remembers "soundcard use files" setting
   ↓
5. Parse stdout for status:
   - "in progress" → RINGING
   - "connected" → ACTIVE
   - "Media streams established" → Confirm ACTIVE
   ↓
6. When ACTIVE, send: "play /path/to/audio.wav\n"
   - Audio injected into call
   - Remote party hears the audio
   - Can repeat unlimited times
   ↓
7. End call: "terminate\n" then "quit\n"
   - Graceful cleanup
   - Process exits cleanly
```

### Why "soundcard use files" is Critical

**Without this command:**
- linphonec uses system audio devices (ALSA/PulseAudio)
- `play` command fails: "Cannot play file: the stream hasn't been started with audio_stream_start_with_files"

**With this command:**
- linphonec uses file-based audio backend
- `play` command works correctly
- Audio is injected into RTP stream
- Remote party hears the audio

**Must be called:**
- ✅ BEFORE making the call
- ✅ In the same linphonec session
- ✅ Only once per session (persists)

---

## 🎓 Best Practices

### Call Management

1. **Always check call status before operations:**
```bash
# Before inject-audio or end
curl http://192.168.1.80:8000/api/v1/call/status
```

2. **Handle call timeouts gracefully:**
```python
import requests
from requests.exceptions import Timeout

try:
    response = requests.post(url, json=data, timeout=5)
except Timeout:
    print("API request timed out")
```

3. **Monitor logs for debugging:**
```bash
# Keep logs.sh output handy
./scripts/logs.sh > debug_output.txt
```

### Audio Management

1. **Test audio files before production:**
```bash
# Test with short call
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{"destination":"sip:test@...", "duration":30, "audio_file":"test.wav"}'
```

2. **Use clear audio filenames:**
```
✅ greeting_welcome_message.wav
✅ menu_main_options.wav
❌ audio1.wav
❌ test.wav
```

3. **Keep audio files organized:**
```
assets/audio/
├── greetings/
│   ├── welcome.wav
│   └── goodbye.wav
├── menus/
│   ├── main_menu.wav
│   └── billing_menu.wav
└── prompts/
    ├── press_1.wav
    └── press_2.wav
```

### Deployment

1. **Test in development first:**
```bash
# Use start.sh for testing
./scripts/start.sh

# Only deploy.sh when ready
sudo ./scripts/deploy.sh
```

2. **Keep backups:**
```bash
# Backup before major changes
tar -czf linphone-caller-backup-$(date +%Y%m%d).tar.gz /opt/linphone-caller
```

3. **Monitor service health:**
```bash
# Add to cron for monitoring
*/5 * * * * curl -f http://localhost:8000/api/v1/health || systemctl restart linphone-caller
```

---

## 🎉 Conclusion

**Linphone Caller is production-ready** with all core features working reliably:

✅ **Call Management** - Start, monitor, and end SIP calls  
✅ **Audio Injection** - Unlimited audio playback during calls  
✅ **Auto-Play** - Automatic audio on answer with configurable delay  
✅ **Logging** - Comprehensive per-call and application logs  
✅ **Deployment** - Easy scripts for installation and updates  
✅ **Stability** - No crashes, auto-restart, boot startup  

**Ready to use in production environments!** 🚀

---

**Developed by:** ratbalas  
**Tested on:** Ubuntu 20.04 LTS  
**VM:** 192.168.1.80  
**Linphone:** linphone-cli (linphonec)  
**Python:** 3.10+  
**Framework:** FastAPI + Uvicorn  
**Date:** December 22, 2025  

---

## 📞 Support & Feedback

For issues, questions, or feature requests, check:
- Application logs: `/opt/linphone-caller/logs/app.log`
- Call logs: `/opt/linphone-caller/logs/calls/`
- Systemd logs: `sudo journalctl -u linphone-caller -n 100`

**Happy Calling!** 🎊
