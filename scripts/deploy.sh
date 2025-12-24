#!/bin/bash
# Deployment script for Linphone Caller as systemd service

set -e

echo "======================================"
echo "Linphone Caller - Deployment Script"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)"
    exit 1
fi

# Get the actual user who ran sudo
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Project root: $PROJECT_ROOT"
echo "Running as user: $ACTUAL_USER"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run ./scripts/install.sh first"
    exit 1
fi

# Create systemd service file
echo "[1/4] Creating systemd service..."
cat > /etc/systemd/system/linphone-caller.service << EOF
[Unit]
Description=Linphone Caller HTTP API
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=$PROJECT_ROOT/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="LINPHONERC=$PROJECT_ROOT/config/linphonerc"
ExecStart=$PROJECT_ROOT/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=linphone-caller

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created at /etc/systemd/system/linphone-caller.service"
echo ""

# Reload systemd
echo "[2/4] Reloading systemd..."
systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

# Enable service
echo "[3/4] Enabling service..."
systemctl enable linphone-caller.service
echo "✓ Service enabled"
echo ""

# Start service
echo "[4/4] Starting service..."
systemctl start linphone-caller.service
echo "✓ Service started"
echo ""

# Check status
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "Service status:"
systemctl status linphone-caller.service --no-pager || true
echo ""
echo "Useful commands:"
echo "  sudo systemctl start linphone-caller    # Start service"
echo "  sudo systemctl stop linphone-caller     # Stop service"
echo "  sudo systemctl restart linphone-caller  # Restart service"
echo "  sudo systemctl status linphone-caller   # Check status"
echo "  sudo journalctl -u linphone-caller -f   # View logs"
echo ""
echo "API Documentation:"
echo "  http://localhost:8000/docs"
echo ""

