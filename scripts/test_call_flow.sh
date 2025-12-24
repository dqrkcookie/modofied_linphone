#!/bin/bash
# Test script for full call flow

set -e

API_BASE="http://localhost:8000/api/v1"

echo "🧪 Testing Linphone SIP Audio Injector"
echo "======================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "\n${YELLOW}Test 1: Health Check${NC}"
response=$(curl -s ${API_BASE}/health)
if echo "$response" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "$response"
    exit 1
fi

# Test 2: Start Call
echo -e "\n${YELLOW}Test 2: Start Call${NC}"
read -p "Enter SIP destination (e.g., sip:1234@example.com): " destination
if [ -z "$destination" ]; then
    echo -e "${RED}✗ Destination required${NC}"
    exit 1
fi

response=$(curl -s -X POST ${API_BASE}/call/start \
    -H 'Content-Type: application/json' \
    -d "{
        \"destination\": \"${destination}\",
        \"duration\": 120
    }")

if echo "$response" | grep -q '"call_id"'; then
    call_id=$(echo "$response" | grep -o '"call_id":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ Call started: ${call_id}${NC}"
else
    echo -e "${RED}✗ Call start failed${NC}"
    echo "$response"
    exit 1
fi

# Wait for call to connect
echo "⏳ Waiting for call to connect..."
sleep 5

# Test 3: Check Status
echo -e "\n${YELLOW}Test 3: Check Call Status${NC}"
response=$(curl -s ${API_BASE}/call/status)
if echo "$response" | grep -q '"status":"active"'; then
    echo -e "${GREEN}✓ Call is active${NC}"
else
    echo -e "${YELLOW}⚠ Call status: $(echo "$response" | grep -o '"status":"[^"]*' | cut -d'"' -f4)${NC}"
fi

# Test 4: Inject Audio
echo -e "\n${YELLOW}Test 4: Inject Audio${NC}"
echo "Available audio files:"
ls -1 assets/audio/*.wav 2>/dev/null | xargs -n1 basename || echo "No audio files found"

read -p "Enter audio file name (or press Enter to skip): " audio_file
if [ -n "$audio_file" ]; then
    response=$(curl -s -X POST ${API_BASE}/call/playAudio \
        -H 'Content-Type: application/json' \
        -d "{
            \"audio_file\": \"${audio_file}\",
            \"silence_after_seconds\": 1.5
        }")
    
    if echo "$response" | grep -q '"message":"Audio injection started successfully"'; then
        echo -e "${GREEN}✓ Audio injection started${NC}"
        echo "⏳ Waiting for audio to complete..."
        sleep 8
    else
        echo -e "${RED}✗ Audio injection failed${NC}"
        echo "$response"
    fi
else
    echo "⏭ Skipping audio injection"
fi

# Test 5: End Call
echo -e "\n${YELLOW}Test 5: End Call${NC}"
read -p "Press Enter to end call..."
response=$(curl -s -X POST ${API_BASE}/call/end)

if echo "$response" | grep -q '"message":"Call ended successfully"'; then
    echo -e "${GREEN}✓ Call ended successfully${NC}"
    
    # Show log file location
    log_file=$(echo "$response" | grep -o '"log_file":"[^"]*' | cut -d'"' -f4)
    echo "📋 Log file: ${log_file}"
else
    echo -e "${RED}✗ Call end failed${NC}"
    echo "$response"
    exit 1
fi

echo -e "\n${GREEN}✅ All tests passed!${NC}"

