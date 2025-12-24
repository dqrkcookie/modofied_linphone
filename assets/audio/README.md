# Audio Files Directory

This directory contains WAV audio files for injection into calls.

## Files

### silence.wav
**Purpose:** Used internally to stop background audio/comfort noise when call starts.
**Format:** 8kHz, Mono, 16-bit PCM
**Duration:** 1 second
**DO NOT DELETE:** This file is required for proper call initialization.

## Adding Your Own Audio Files

1. **Format Requirements:**
   - Format: WAV
   - Sample Rate: 8-48kHz (8kHz recommended for VoIP)
   - Channels: Mono or Stereo
   - Bit Depth: 16-bit PCM

2. **Upload to VM:**
   ```bash
   scp your_audio.wav administrator@192.168.1.80:/opt/linphone-caller/assets/audio/
   ```

3. **Use in API:**
   ```bash
   curl -X POST http://192.168.1.80:8000/api/v1/call/playAudio \
     -H 'Content-Type: application/json' \
     -d '{"audio_file":"your_audio.wav"}'
   ```

## Examples

- `greeting.wav` - Welcome message
- `menu_options.wav` - IVR menu
- `thank_you.wav` - Closing message
- `silence.wav` - Internal use (background noise suppression)


