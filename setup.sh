#!/bin/bash

# Algorithm Development and Analysis Platform Setup Script

# Set up colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Algorithm Platform Setup ===${NC}"
echo -e "${BLUE}=============================${NC}"
echo

# Base directory
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATA_DIR="$BASE_DIR/data"
SCRIPTS_DIR="$BASE_DIR/scripts"
REPORTS_DIR="$BASE_DIR/reports"
DOCS_DIR="$BASE_DIR/docs"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo -e "${RED}Error: pip is not installed.${NC}"
    echo -e "${YELLOW}Please install pip before continuing.${NC}"
    exit 1
fi

# Create required directories
echo -e "${BLUE}Creating project directories...${NC}"
mkdir -p "$DATA_DIR"
mkdir -p "$REPORTS_DIR"
mkdir -p "$DOCS_DIR"
mkdir -p "$DOCS_DIR/obsidian_export"

echo -e "${GREEN}Directory structure created.${NC}"

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install matplotlib numpy pandas

if [ $? -ne 0 ]; then
    echo -e "${RED}Warning: Some dependencies could not be installed.${NC}"
    echo -e "${YELLOW}The platform will still work, but visualization features may be limited.${NC}"
else
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
fi

# Initialize the database
echo -e "${BLUE}Initializing the database...${NC}"
python "$SCRIPTS_DIR/init_database.py"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Database initialization failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Database initialized successfully.${NC}"

# Generate preview image
echo -e "${BLUE}Generating preview image...${NC}"
python "$SCRIPTS_DIR/generate_preview.py"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Warning: Could not generate preview image.${NC}"
    echo -e "${YELLOW}This is not critical for the platform functionality.${NC}"
else
    echo -e "${GREEN}Preview image generated successfully.${NC}"
fi

# Make scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x "$BASE_DIR/algo_platform.sh"
chmod +x "$BASE_DIR/run.py"
chmod +x "$SCRIPTS_DIR/init_database.py"
chmod +x "$SCRIPTS_DIR/export_to_obsidian.py"

echo -e "${GREEN}Setup completed successfully!${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Run the platform: ${GREEN}./algo_platform.sh${NC}"
echo -e "2. Or use the command-line interface: ${GREEN}./run.py test${NC}"
echo
echo -e "${YELLOW}Enjoy your algorithm development and analysis platform!${NC}"
