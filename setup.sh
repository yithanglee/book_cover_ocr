#!/bin/bash
# Quick setup script for Book Cover OCR Service on GMKtec M3

set -e

echo "=========================================="
echo "Book Cover OCR Service - Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}This script is designed for Linux. Please run on Ubuntu/Debian.${NC}"
    exit 1
fi

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo -e "${RED}Python 3.8+ required. Found: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version found${NC}"

# Install system dependencies
echo -e "\n${YELLOW}Installing system dependencies...${NC}"
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq libgl1-mesa-glx libglib2.0-0 python3-pip python3-venv
    echo -e "${GREEN}✓ System dependencies installed${NC}"
fi

# Create virtual environment
echo -e "\n${YELLOW}Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Make scripts executable
echo -e "\n${YELLOW}Making scripts executable...${NC}"
chmod +x batch_process.py watch_folder.py client_example.py
echo -e "${GREEN}✓ Scripts are now executable${NC}"

# Check required files
echo -e "\n${YELLOW}Checking required files...${NC}"
required_files=("embeddings.npy" "meta.json" "models/mobilenet.onnx")
all_files_present=true

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ Found: $file${NC}"
    else
        echo -e "${RED}✗ Missing: $file${NC}"
        all_files_present=false
    fi
done

if [ "$all_files_present" = false ]; then
    echo -e "${RED}Some required files are missing. Please ensure all model files are present.${NC}"
    exit 1
fi

# Get IP address
echo -e "\n${YELLOW}Network Information:${NC}"
ip_address=$(hostname -I | awk '{print $1}')
echo -e "Local IP: ${GREEN}$ip_address${NC}"

# Summary
echo -e "\n=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "=========================================="
echo ""
echo "To start the service:"
echo -e "${YELLOW}  source venv/bin/activate${NC}"
echo -e "${YELLOW}  uvicorn app:app --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "Access points:"
echo "  Local:   http://localhost:8000"
echo "  Network: http://$ip_address:8000"
echo ""
echo "Documentation:"
echo "  - README.md       - General usage guide"
echo "  - DEPLOYMENT.md   - Detailed deployment steps"
echo ""
echo "Tools available:"
echo "  - batch_process.py  - Batch process images"
echo "  - watch_folder.py   - Monitor folder for new images"
echo "  - client_example.py - Example API client"
echo ""
echo -e "${GREEN}Happy book scanning! 📚${NC}"

