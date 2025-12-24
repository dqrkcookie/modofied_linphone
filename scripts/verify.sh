#!/bin/bash
# Check project structure and report status

echo "Linphone Caller - Project Verification"
echo "======================================="
echo ""

# Function to check if file/dir exists
check_exists() {
    if [ -e "$1" ]; then
        echo "✓ $1"
        return 0
    else
        echo "✗ $1 (MISSING)"
        return 1
    fi
}

cd "$(dirname "$0")/.."

echo "Core Application:"
check_exists "app/main.py"
check_exists "app/api/routes.py"
check_exists "app/core/config.py"
check_exists "app/core/linphone_controller.py"
check_exists "app/models/schemas.py"

echo ""
echo "Configuration:"
check_exists ".env.example"
check_exists "requirements.txt"
check_exists "config/linphonerc"

echo ""
echo "Scripts:"
check_exists "scripts/install.sh"
check_exists "scripts/deploy.sh"
check_exists "scripts/start.sh"

echo ""
echo "Directories:"
check_exists "assets/audio"
check_exists "logs"

echo ""
echo "Documentation:"
check_exists "README.md"
check_exists "QUICKSTART.md"
check_exists "DEPLOYMENT.md"
check_exists "API_EXAMPLES.md"
check_exists "AUDIO_GUIDE.md"

echo ""
echo "Tests & Examples:"
check_exists "tests/test_api.py"
check_exists "examples/test_client.py"

echo ""
echo "======================================="

# Check if .env exists
if [ -f ".env" ]; then
    echo "✓ Configuration file (.env) exists"
else
    echo "⚠ Configuration file (.env) not found"
    echo "  Run: cp .env.example .env"
fi

# Check for audio files
AUDIO_COUNT=$(ls -1 assets/audio/*.wav 2>/dev/null | wc -l)
if [ $AUDIO_COUNT -gt 0 ]; then
    echo "✓ Found $AUDIO_COUNT audio file(s)"
else
    echo "⚠ No audio files found in assets/audio/"
    echo "  Add .wav files to assets/audio/ directory"
fi

echo ""
echo "Next Steps:"
echo "1. Copy and configure .env: cp .env.example .env && nano .env"
echo "2. Add audio files: cp /path/to/*.wav assets/audio/"
echo "3. Install: ./scripts/install.sh"
echo "4. Start server: ./scripts/start.sh"
echo "5. Test: curl http://localhost:8000/api/v1/health"
echo ""

