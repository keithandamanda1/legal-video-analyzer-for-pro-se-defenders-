#!/usr/bin/env bash
# Start the Legal Video Analyzer
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Run setup.sh first."
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║    Legal Video Analyzer — Pro Se Defense Tool            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  Starting application..."
echo "  Open your browser to: http://127.0.0.1:5000"
echo ""
echo "  Free legal help in Maine:"
echo "  Pine Tree Legal Assistance:  207-774-8211"
echo "  Maine Legal Services:        1-800-750-5353"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

python3 app.py
