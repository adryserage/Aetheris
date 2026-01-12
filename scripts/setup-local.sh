#!/usr/bin/env bash
# =============================================================================
# Aetheris Local Setup Script (Linux/macOS)
# =============================================================================
#
# This script helps you set up Aetheris locally to view and run analysis
# from CI/CD artifacts or fresh installations.
#
# Usage:
#   chmod +x setup-local.sh
#   ./setup-local.sh
#
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Aetheris Local Setup                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
echo -e "${BLUE}[1/4]${NC} Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION found"
    else
        echo -e "  ${RED}✗${NC} Python 3.9+ required (found $PYTHON_VERSION)"
        exit 1
    fi
else
    echo -e "  ${RED}✗${NC} Python 3 not found"
    echo "  Please install Python 3.9 or higher:"
    echo "    - macOS: brew install python@3.11"
    echo "    - Ubuntu: sudo apt install python3.11"
    exit 1
fi

# Check if Aetheris is installed
echo -e "${BLUE}[2/4]${NC} Checking Aetheris installation..."
if python3 -c "import aetheris" &> /dev/null 2>&1 || command -v aetheris &> /dev/null; then
    AETHERIS_VERSION=$(aetheris --version 2>/dev/null || echo "installed")
    echo -e "  ${GREEN}✓${NC} Aetheris $AETHERIS_VERSION found"
else
    echo -e "  ${YELLOW}!${NC} Aetheris not installed"
    echo -e "  Installing..."
    pip3 install adryserage-aetheris
    echo -e "  ${GREEN}✓${NC} Aetheris installed"
fi

# Check API key
echo -e "${BLUE}[3/4]${NC} Checking API key configuration..."
if [ -n "$GEMINI_API_KEY" ] || [ -n "$OPENAI_API_KEY" ] || [ -n "$ANTHROPIC_API_KEY" ]; then
    echo -e "  ${GREEN}✓${NC} API key found in environment"
else
    echo -e "  ${YELLOW}!${NC} No API key found"
    echo ""
    echo "  To run analyses, you need an AI API key."
    echo "  Set one of the following environment variables:"
    echo ""
    echo "    export GEMINI_API_KEY=your_key_here     # Recommended (free tier)"
    echo "    export OPENAI_API_KEY=your_key_here"
    echo "    export ANTHROPIC_API_KEY=your_key_here"
    echo ""
    echo "  Get a free Gemini API key: https://ai.google.dev"
    echo ""
fi

# Check for analysis results
echo -e "${BLUE}[4/4]${NC} Checking for analysis results..."
if [ -d "docs/analyses" ]; then
    FILE_COUNT=$(find docs/analyses -name "*.md" 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓${NC} Found $FILE_COUNT analysis reports in docs/analyses/"
    echo ""
    echo -e "${GREEN}Analysis results available!${NC}"
    echo "  Open docs/analyses/ in your browser or Markdown viewer"
elif [ -d "../docs/analyses" ]; then
    FILE_COUNT=$(find ../docs/analyses -name "*.md" 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓${NC} Found $FILE_COUNT analysis reports in ../docs/analyses/"
    echo ""
    echo -e "${GREEN}Analysis results available!${NC}"
    echo "  Open ../docs/analyses/ in your browser or Markdown viewer"
else
    echo -e "  ${YELLOW}!${NC} No analysis results found"
    echo ""
    echo "  Run Aetheris to generate analysis:"
    echo "    aetheris analysis"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Quick commands:"
echo "  aetheris analysis                    # Run full analysis"
echo "  aetheris analysis --reanalyze        # Analyze changed files only"
echo "  aetheris analysis --profile safe     # Run in safe mode"
echo "  aetheris stats                       # View statistics"
echo ""
echo "Documentation: https://adryserage.github.io/aetheris/"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
