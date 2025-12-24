#!/bin/bash

#################################################################################
# Linphone Caller - Quick Update Script (Run on VM)
# Run this script ON THE VM after syncing files
#################################################################################

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Linphone Caller - Update${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Change to app directory
cd /opt/linphone-caller || { echo "Error: /opt/linphone-caller not found"; exit 1; }

# Step 1: Clear Python cache
echo -e "${YELLOW}[1/3]${NC} Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✓${NC} Cache cleared"
echo ""

# Step 2: Restart service
echo -e "${YELLOW}[2/3]${NC} Restarting linphone-caller service..."
sudo systemctl restart linphone-caller
echo -e "${GREEN}✓${NC} Service restarted"
echo ""

# Step 3: Wait and check status
echo -e "${YELLOW}[3/3]${NC} Checking service status..."
sleep 2

if sudo systemctl is-active --quiet linphone-caller; then
    echo -e "${GREEN}✓${NC} Service is running"
    echo ""
    echo -e "${BLUE}Service Status:${NC}"
    sudo systemctl status linphone-caller --no-pager -l | head -20
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}  ✅ Update Complete!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo -e "Health Check: ${BLUE}curl http://localhost:8000/api/v1/health${NC}"
else
    echo -e "${RED}✗${NC} Service failed to start!"
    echo ""
    echo -e "${RED}Error logs:${NC}"
    sudo journalctl -u linphone-caller -n 30 --no-pager
    exit 1
fi

