#!/bin/bash
# Simple bash client example

API_URL="http://localhost:8000/api/v1"

echo "Linphone Caller - Bash Test Client"
echo "===================================="

# Health check
echo ""
echo "1. Checking health..."
HEALTH=$(curl -s $API_URL/health)
echo "$HEALTH" | jq '.'

# Get user input
echo ""
echo "2. Enter call details:"
read -p "   SIP Destination: " DESTINATION
read -p "   Duration (default 120): " DURATION
DURATION=${DURATION:-120}

# Start call
echo ""
echo "3. Starting call..."
CALL_RESPONSE=$(curl -s -X POST $API_URL/call/start \
  -H "Content-Type: application/json" \
  -d "{\"destination\":\"$DESTINATION\",\"duration\":$DURATION}")

echo "$CALL_RESPONSE" | jq '.'

CALL_ID=$(echo "$CALL_RESPONSE" | jq -r '.call_id')

if [ "$CALL_ID" == "null" ] || [ -z "$CALL_ID" ]; then
    echo "ERROR: Failed to start call"
    exit 1
fi

echo "Call ID: $CALL_ID"

# Wait
echo ""
echo "4. Waiting 5 seconds..."
sleep 5

# Check status
echo ""
echo "5. Checking status..."
curl -s $API_URL/call/$CALL_ID/status | jq '.'

# Audio injection
echo ""
read -p "6. Inject audio? (y/n): " INJECT

if [ "$INJECT" == "y" ]; then
    read -p "   Audio file name: " AUDIO_FILE
    echo "   Injecting audio..."
    curl -s -X POST $API_URL/call/$CALL_ID/inject-audio \
      -H "Content-Type: application/json" \
      -d "{\"audio_file_name\":\"$AUDIO_FILE\"}" | jq '.'
fi

# End call
echo ""
read -p "7. End call now? (y/n): " END_CALL

if [ "$END_CALL" == "y" ]; then
    echo "   Ending call..."
    curl -s -X POST $API_URL/call/$CALL_ID/end | jq '.'
else
    echo "   Call will continue..."
fi

echo ""
echo "===================================="
echo "Test complete!"

