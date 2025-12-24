#!/bin/bash
# Installation script for Linphone Caller

set -e

echo "======================================"
echo "Linphone Caller - Installation Script"
echo "======================================"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Error: This script must be run on Linux"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

echo "Current directory: $PROJECT_ROOT"
echo ""

# Display pre-requisites information
echo "======================================"
echo "PRE-REQUISITES CHECK"
echo "======================================"
echo ""
echo "Before running this script, ensure you have completed these steps:"
echo ""
echo "1️⃣  System packages should be installed:"
echo "   sudo apt-get update"
echo "   sudo apt-get install -y python3 python3-pip python3-venv linphone-cli build-essential curl jq"
echo ""
echo "2️⃣  Files should be deployed to a proper location:"
echo "   Recommended locations:"
echo "     - Production:  /opt/linphone-caller"
echo "     - Development: /home/\$USER/linphone-caller"
echo "   Current location: $PROJECT_ROOT"
echo ""
echo "3️⃣  Scripts should have execute permissions:"
echo "   chmod +x scripts/*.sh"
echo ""
echo "======================================"
echo ""

# Verify current location
if [[ "$PROJECT_ROOT" == "/tmp"* ]]; then
    echo "⚠️  WARNING: You're running from /tmp directory!"
    echo "   This location may be cleared on reboot."
    echo "   Recommended: Deploy to /opt/linphone-caller or /home/\$USER/linphone-caller"
    echo ""
    read -p "Do you want to continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo "Installation cancelled."
        exit 0
    fi
    echo ""
fi

# Check if script has execute permission (informational)
if [ ! -x "$SCRIPT_DIR/install.sh" ]; then
    echo "ℹ️  Note: Scripts don't have execute permissions yet."
    echo "   Run: chmod +x scripts/*.sh"
    echo ""
fi

echo "Starting installation checks..."
echo ""

# Check if service is running and stop it
echo "[Pre-install] Checking for running service..."
if systemctl is-active --quiet linphone-caller 2>/dev/null; then
    echo "⚠ Service is running. Stopping..."
    sudo systemctl stop linphone-caller
    echo "✓ Service stopped"
elif [ -f "/etc/systemd/system/linphone-caller.service" ]; then
    echo "ℹ️  Service exists but is not running"
else
    echo "ℹ️  Service not installed yet"
fi
echo ""

# Remove old virtual environment
echo "[Pre-install] Cleaning up old virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Removing old venv directory..."
    rm -rf venv
    echo "✓ Old venv removed"
else
    echo "ℹ️  No venv to remove"
fi
echo ""

# Remove Python cache files
echo "[Pre-install] Removing Python cache files..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "✓ Python cache cleared"
echo ""

# Check if linphone-cli is installed
echo "[1/7] Checking for linphone-cli..."
if command -v linphonecsh &> /dev/null; then
    echo "✓ linphonecsh found at: $(which linphonecsh)"
elif command -v linphonec &> /dev/null; then
    echo "✓ linphonec found at: $(which linphonec)"
    echo "⚠ Warning: linphonecsh is recommended over linphonec"
else
    echo "✗ Error: linphone-cli not found"
    echo ""
    echo "Please install linphone-cli:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y linphone-cli"
    exit 1
fi
echo ""

# Check if Python 3.8+ is installed
echo "[2/7] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Error: Python 3 not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "✗ Error: Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment (always fresh since we cleaned up)
echo "[3/7] Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "[4/7] Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✗ Error: Could not find venv/bin/activate"
    exit 1
fi
echo ""

# Upgrade pip
echo "[5/7] Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "[6/7] Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create necessary directories
echo "[7/7] Creating directories..."
mkdir -p assets/audio
mkdir -p logs
mkdir -p config
echo "✓ Directories created"
echo ""

# Create basic linphonerc if it doesn't exist
echo "[8/8] Setting up linphone configuration..."
if [ ! -f "config/linphonerc" ]; then
    cat > config/linphonerc << 'EOF'
[sip]
default_proxy=0
register_only_when_network_is_up=1
register_only_when_upnp_is_ok=1

[rtp]
audio_rtp_port=7078
video_rtp_port=9078

[sound]
echocancellation=0
playback_dev_id=ALSA: default device
capture_dev_id=ALSA: default device

[video]
enabled=0

[net]
mtu=1300
EOF
    echo "✓ Linphone config created"
else
    echo "✓ Linphone config already exists"
fi
echo ""

echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Summary:"
echo "  ✓ Old service stopped (if running)"
echo "  ✓ Old venv removed"
echo "  ✓ Python cache cleared"
echo "  ✓ Fresh virtual environment created"
echo "  ✓ Dependencies installed"
echo "  ✓ Directories created"
echo "  ✓ Linphone config created"
echo ""
echo "Configuration:"
echo "  • Server settings in: app/core/config.py (defaults)"
echo "  • Linphone settings in: config/linphonerc"
echo "  • No .env file needed!"
echo ""
echo "Next steps:"
echo "1. (Optional) Add audio files (.wav) to:"
echo "   assets/audio/"
echo ""
echo "2. Start/Restart the service:"
echo "   sudo systemctl start linphone-caller"
echo ""
echo "3. Check status:"
echo "   sudo systemctl status linphone-caller"
echo "   curl http://localhost:8000/api/v1/health"
echo ""
echo "4. Make a test call:"
echo "   curl -X POST http://localhost:8000/api/v1/call/start -d '{\"destination\":\"sip:1009999@YOUR_SIP_SERVER_IP:5060\"}'"
echo ""

