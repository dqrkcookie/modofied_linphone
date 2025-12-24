# Configuration Guide

This guide helps you configure the Linphone Caller API for your environment.

## 🌐 Network Configuration

Throughout the documentation, you'll see placeholder values that need to be replaced with your actual network information:

### Placeholder Reference

| Placeholder | Description | Example |
|------------|-------------|---------|
| `YOUR_SERVER_IP` | The IP address of the server running the Linphone Caller API | `192.168.1.80` or `10.0.1.100` |
| `YOUR_SIP_SERVER_IP` | The IP address of your SIP server/PBX | `192.168.1.40` or `sip.example.com` |
| `YOUR_USERNAME` | Your SSH username for remote server access | `administrator`, `ubuntu`, `deploy` |
| `YOUR_NETWORK_RANGE` | Your network CIDR range for firewall rules | `192.168.1.0` or `10.0.0.0` |

### Example Replacements

**Before:**
```bash
curl -X POST http://YOUR_SERVER_IP:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{"destination": "sip:1001@YOUR_SIP_SERVER_IP:5060"}'
```

**After (with your actual values):**
```bash
curl -X POST http://192.168.1.80:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{"destination": "sip:1001@192.168.1.40:5060"}'
```

## 🔧 Configuration Files

### 1. Application Configuration (`app/core/config.py`)

The default host binding is `0.0.0.0` which means the API will listen on all network interfaces. This is typically what you want.

```python
HOST: str = "0.0.0.0"  # Listens on all interfaces
PORT: int = 8000        # Default API port
```

### 2. Linphone Configuration (`config/linphonerc`)

Configure your SIP account credentials in this file:

```ini
[sip]
default_proxy=0
register_only_when_network_is_up=1
guess_hostname=1

[proxy_0]
reg_proxy=<sip:YOUR_SIP_SERVER_IP>
reg_identity=sip:YOUR_SIP_USERNAME@YOUR_SIP_SERVER_IP
reg_expires=3600
reg_sendregister=1
publish=0
dial_escape_plus=0
```

**Replace:**
- `YOUR_SIP_SERVER_IP` - Your SIP server address (e.g., `192.168.1.40`)
- `YOUR_SIP_USERNAME` - Your SIP extension/username (e.g., `1000`)

### 3. Environment Variables (`.env`)

Create a `.env` file in the project root:

```env
# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

# Linphone Paths
LINPHONE_BINARY=/usr/bin/linphonec
LINPHONE_CONFIG=/opt/linphone-caller/config/linphonerc

# Directory Paths
AUDIO_DIRECTORY=/opt/linphone-caller/assets/audio
LOG_DIRECTORY=/opt/linphone-caller/logs
```

## 🔐 Firewall Configuration

If you're running a firewall, you need to allow access to the API port:

### Allow from Specific Network
```bash
# Replace YOUR_NETWORK_RANGE with your network (e.g., 192.168.1.0)
sudo ufw allow from YOUR_NETWORK_RANGE/24 to any port 8000
```

### Allow from Anywhere (Less Secure)
```bash
sudo ufw allow 8000/tcp
```

### SIP Ports (if running SIP server on same machine)
```bash
sudo ufw allow 5060/udp  # SIP signaling
sudo ufw allow 5061/tcp  # SIP over TLS
sudo ufw allow 10000:20000/udp  # RTP media ports
```

## 🌍 DNS and Hostnames

Instead of IP addresses, you can use hostnames if you have DNS configured:

**API Server:**
```bash
# Instead of: http://192.168.1.80:8000
# Use: http://linphone-api.example.com:8000
```

**SIP Server:**
```bash
# Instead of: sip:1001@192.168.1.40:5060
# Use: sip:1001@sip.example.com:5060
```

## 📡 Remote Deployment

When deploying to a remote server, replace the SSH commands:

### File Transfer
```bash
# Upload audio files
scp your_audio.wav YOUR_USERNAME@YOUR_SERVER_IP:/opt/linphone-caller/assets/audio/

# Deploy entire project
rsync -avz linphone-caller/ YOUR_USERNAME@YOUR_SERVER_IP:/opt/linphone-caller/
```

### Remote Access
```bash
# SSH into server
ssh YOUR_USERNAME@YOUR_SERVER_IP

# Check logs remotely
ssh YOUR_USERNAME@YOUR_SERVER_IP "tail -f /opt/linphone-caller/logs/app.log"
```

## 🧪 Testing Your Configuration

After configuration, test your setup:

### 1. Health Check
```bash
curl http://YOUR_SERVER_IP:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "linphone_available": true
}
```

### 2. Test Call
```bash
curl -X POST http://YOUR_SERVER_IP:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "sip:EXTENSION@YOUR_SIP_SERVER_IP:5060",
    "duration": 30
  }'
```

### 3. Check Status
```bash
curl http://YOUR_SERVER_IP:8000/api/v1/call/status
```

## 🚨 Common Issues

### Issue: Cannot connect to API
- **Check:** Is the service running? `sudo systemctl status linphone-caller`
- **Check:** Is the firewall blocking? `sudo ufw status`
- **Check:** Is the port correct? Default is `8000`

### Issue: SIP registration fails
- **Check:** Is `YOUR_SIP_SERVER_IP` correct in `config/linphonerc`?
- **Check:** Are credentials correct?
- **Check:** Can you reach the SIP server? `ping YOUR_SIP_SERVER_IP`

### Issue: Calls don't connect
- **Check:** Is the destination format correct? Should be `sip:EXTENSION@SERVER:PORT`
- **Check:** Is Linphone registered? Check logs: `tail -f logs/app.log`
- **Check:** Are SIP ports open on firewall?

## 📞 Example Production Setup

Here's a complete example with real (example) values:

**Scenario:**
- API Server: `10.0.1.100`
- SIP Server: `10.0.1.50`
- SIP Extension: `1001`
- Network: `10.0.1.0/24`

**Commands:**
```bash
# Health check
curl http://10.0.1.100:8000/api/v1/health

# Start call
curl -X POST http://10.0.1.100:8000/api/v1/call/start \
  -H 'Content-Type: application/json' \
  -d '{"destination": "sip:1001@10.0.1.50:5060"}'

# Firewall rule
sudo ufw allow from 10.0.1.0/24 to any port 8000

# SSH access
ssh admin@10.0.1.100

# Upload audio
scp custom_audio.wav admin@10.0.1.100:/opt/linphone-caller/assets/audio/
```

## 📚 Additional Resources

- [README.md](README.md) - Main documentation
- [PRODUCTION_READY.md](PRODUCTION_READY.md) - Full production deployment guide
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick command reference

---

**Need Help?** Check the logs at `logs/app.log` or enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

