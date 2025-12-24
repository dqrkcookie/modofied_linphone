# Changelog

All notable changes to the Linphone SIP Audio Injector project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-24

### Added
- ✨ Initial release of Linphone SIP Audio Injector
- 🎯 HTTP REST API for SIP call management
- 🎵 Non-blocking audio injection with interruption support
- 📊 RTP stream segmentation for transcription systems
- 🔧 Auto-play audio on call answer
- 📝 Per-call detailed logging
- 🏥 Health check endpoint
- 🐳 Docker support
- ⚙️ Systemd service for production deployment
- 📖 Comprehensive documentation

### Features
- Start outbound SIP calls via API
- Inject unlimited audio files during active calls
- Configurable silence gaps for RTP segmentation
- Audio interruption (newest audio replaces current)
- Real-time call status monitoring
- Graceful call termination
- Automatic cleanup of zombie processes
- WAV file format support (8-48kHz, mono/stereo)

### API Endpoints
- `POST /call/start` - Initiate SIP call
- `GET /call/status` - Get current call status
- `POST /call/playAudio` - Inject audio into call
- `POST /call/end` - Terminate call
- `GET /health` - Health check

### Technical
- Built with FastAPI and asyncio
- Uses linphonec for SIP protocol
- Python 3.8+ compatibility
- Robust error handling
- Process lifecycle management
- Background task coordination

---

## [Unreleased]

### Planned Features
- WebSocket support for real-time events
- Multiple concurrent calls support
- Audio format auto-conversion (MP3, OGG → WAV)
- Call recording capabilities
- Prometheus metrics export
- Kubernetes deployment manifests
- Web-based admin panel
- DTMF tone injection
- Call transfer capabilities

---

## Version History

- **1.0.0** (2025-12-24) - Initial public release

---

For more details, see the [README.md](README.md) and [PRODUCTION_READY.md](PRODUCTION_READY.md).

