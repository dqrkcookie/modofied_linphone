#!/bin/bash
# Stop the linphone-caller service

set -e

echo "Stopping Linphone Caller service..."

if systemctl is-active --quiet linphone-caller.service; then
    sudo systemctl stop linphone-caller.service
    echo "✓ Service stopped"
else
    echo "Service is not running"
fi

