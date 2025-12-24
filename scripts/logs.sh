#!/bin/bash
# View logs for linphone-caller service

set -e

if systemctl is-active --quiet linphone-caller.service; then
    echo "Showing logs for linphone-caller (Ctrl+C to exit)..."
    echo ""
    sudo journalctl -u linphone-caller -f
else
    echo "Service is not running"
    echo "Showing last 50 lines of logs:"
    echo ""
    sudo journalctl -u linphone-caller -n 50
fi

