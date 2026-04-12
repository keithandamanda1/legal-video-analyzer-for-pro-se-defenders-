#!/usr/bin/env bash
# =============================================================================
#  Legal Video Analyzer — Automated Setup Script
#  Installs all required system dependencies and Python packages.
#  Run once: bash setup.sh
# =============================================================================

set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo ""
echo -e "${BOLD}${YELLOW}╔══════════════════════════════════════════════════════════╗"
echo -e "║    Legal Video Analyzer — Pro Se Defense Tool Setup      ║"
echo -e "╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Check we're in the right directory ───────────────────────────────────────
if [ ! -f "app.py" ]; then
    echo -e "${RED}ERROR: Run this script from the project directory (where app.py is).${NC}"
    exit 1
fi

# ── Detect OS ─────────────────────────────────────────────────────────────────
OS="unknown"
if [ -f /etc/debian_version ] || grep -qi ubuntu /etc/os-release 2>/dev/null; then
    OS="debian"
elif [ -f /etc/redhat-release ] || grep -qi fedora /etc/os-release 2>/dev/null; then
    OS="redhat"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
fi
echo -e "${BLUE}Detected OS: $OS${NC}"

# ── Step 1: Install system dependencies ──────────────────────────────────────
echo ""
echo -e "${YELLOW}[1/5] Installing system dependencies (ffmpeg, python3)...${NC}"

if command -v ffmpeg &>/dev/null; then
    echo -e "${GREEN}  ✓ ffmpeg already installed: $(ffmpeg -version 2>&1 | head -1)${NC}"
else
    echo -e "${BLUE}  Installing ffmpeg...${NC}"
    if [ "$OS" = "debian" ]; then
        sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg
    elif [ "$OS" = "redhat" ]; then
        sudo dnf install -y ffmpeg || sudo yum install -y ffmpeg
    elif [ "$OS" = "macos" ]; then
        if command -v brew &>/dev/null; then
            brew install ffmpeg
        else
            echo -e "${RED}  Homebrew not found. Install ffmpeg manually: https://ffmpeg.org/download.html${NC}"
        fi
    else
        echo -e "${RED}  Could not auto-install ffmpeg. Please install it manually.${NC}"
        echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
        echo "  CentOS/RHEL:   sudo yum install ffmpeg"
        echo "  macOS:         brew install ffmpeg"
    fi
fi

# Check python3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}  python3 not found. Installing...${NC}"
    if [ "$OS" = "debian" ]; then
        sudo apt-get install -y -qq python3 python3-pip python3-venv
    fi
else
    echo -e "${GREEN}  ✓ Python3: $(python3 --version)${NC}"
fi

# ── Step 2: Create virtual environment ───────────────────────────────────────
echo ""
echo -e "${YELLOW}[2/5] Setting up Python virtual environment...${NC}"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}  ✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}  ✓ Virtual environment exists${NC}"
fi

# Activate venv
source venv/bin/activate

# ── Step 3: Install Python packages ──────────────────────────────────────────
echo ""
echo -e "${YELLOW}[3/5] Installing Python packages...${NC}"

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Verify key packages
python3 -c "import anthropic; print('  ✓ anthropic', anthropic.__version__)" 2>/dev/null || echo -e "${RED}  ✗ anthropic install failed${NC}"
python3 -c "import flask; print('  ✓ flask', flask.__version__)" 2>/dev/null || echo -e "${RED}  ✗ flask install failed${NC}"
python3 -c "import docx; print('  ✓ python-docx')" 2>/dev/null || echo -e "${YELLOW}  ! python-docx not installed (document generation will use text format)${NC}"

echo -e "${GREEN}  ✓ All packages installed${NC}"

# ── Step 4: Create directories ────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[4/5] Creating data directories...${NC}"

mkdir -p data/{uploads,cases,documents,exports}
echo -e "${GREEN}  ✓ Directories created${NC}"

# ── Step 5: Configure API key ─────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[5/5] Configuration...${NC}"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}  Created .env from template${NC}"
fi

# Check if API key is set
if grep -q "sk-ant-your-key-here" .env 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}  ⚠  ANTHROPIC API KEY NOT CONFIGURED${NC}"
    echo -e "     You need an Anthropic API key for the AI video analysis."
    echo -e "     Get one free at: https://console.anthropic.com"
    echo ""
    read -p "  Enter your Anthropic API key (or press Enter to skip): " API_KEY
    if [ -n "$API_KEY" ]; then
        # Update the .env file
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|ANTHROPIC_API_KEY=sk-ant-your-key-here|ANTHROPIC_API_KEY=$API_KEY|" .env
        else
            sed -i "s|ANTHROPIC_API_KEY=sk-ant-your-key-here|ANTHROPIC_API_KEY=$API_KEY|" .env
        fi
        echo -e "${GREEN}  ✓ API key saved to .env${NC}"
    else
        echo -e "${YELLOW}  Skipped — add your key manually to .env before running analysis.${NC}"
    fi
else
    echo -e "${GREEN}  ✓ API key already configured${NC}"
fi

# ── Create run script ─────────────────────────────────────────────────────────
cat > run.sh << 'RUNSCRIPT'
#!/usr/bin/env bash
# Start the Legal Video Analyzer
cd "$(dirname "$0")"
source venv/bin/activate
echo ""
echo "Starting Legal Video Analyzer..."
echo "Open your browser to: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop."
echo ""
python3 app.py
RUNSCRIPT
chmod +x run.sh

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════╗"
echo -e "║            Setup Complete!                               ║"
echo -e "╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  To start the application:"
echo -e "  ${BOLD}bash run.sh${NC}"
echo ""
echo -e "  Or manually:"
echo -e "  ${BOLD}source venv/bin/activate${NC}"
echo -e "  ${BOLD}python3 app.py${NC}"
echo ""
echo -e "  Then open: ${BLUE}http://127.0.0.1:5000${NC}"
echo ""
echo -e "${YELLOW}  Free legal help in Maine:${NC}"
echo -e "  Pine Tree Legal Assistance:  207-774-8211"
echo -e "  Maine Legal Services:        1-800-750-5353"
echo -e "  ACLU of Maine:               207-774-5444"
echo ""
