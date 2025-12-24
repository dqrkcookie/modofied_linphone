# Quick Reference Guide

## 🚀 Start the Server

```bash
# Development
python -m app.main

# Production (systemd)
sudo systemctl start linphone-caller
```

## 📞 Make a Simple Call

```bash
curl -X POST http://localhost:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{"destination": "sip:1234@example.com", "duration": 120}'
```

## 🎵 Inject Audio

```bash
curl -X POST http://localhost:8000/api/v1/call/playAudio \
  -H 'Content-Type: application/json' \
  -d '{"audio_file": "greeting.wav", "silence_after_seconds": 1.5}'
```

## 🛑 End Call

```bash
curl -X POST http://localhost:8000/api/v1/call/end
```

## 📊 Check Status

```bash
# Call status
curl http://localhost:8000/api/v1/call/status

# Health check
curl http://localhost:8000/api/v1/health
```

## 📝 View Logs

```bash
# Main application log
tail -f logs/app.log

# Per-call logs
tail -f logs/calls/call_*.log

# Service logs
sudo journalctl -u linphone-caller -f
```

## 🎯 Common Tasks

### Add Audio File
```bash
cp your_audio.wav assets/audio/
```

### Convert Audio to WAV
```bash
ffmpeg -i input.mp3 -ar 8000 -ac 1 -sample_fmt s16 output.wav
```

### Restart Service
```bash
sudo systemctl restart linphone-caller
```

### Deploy Updates
```bash
./scripts/deploy.sh
```

### Test Call Flow
```bash
./scripts/test_call_flow.sh
```

## 🐛 Troubleshooting

### Kill Zombie Processes
```bash
pkill -9 linphonec
sudo systemctl restart linphone-caller
```

### Check If Linphone Is Installed
```bash
which linphonec
linphonec --version
```

### View API Documentation
```
http://localhost:8000/docs
```

## 🔧 Configuration

### Main Config
```bash
nano config/linphonerc
```

### Environment Variables
```bash
nano .env
```

## 📚 Documentation Files

- `README.md` - Main documentation
- `PRODUCTION_READY.md` - Deployment guide
- `CONTRIBUTING.md` - Contribution guide
- `CHANGELOG.md` - Version history
- `REPOSITORY_READY.md` - Publishing guide

---

**Quick Links:**
- Health: http://localhost:8000/api/v1/health
- API Docs: http://localhost:8000/docs
- Logs: `logs/app.log`

