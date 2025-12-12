#!/bin/bash
# Installation script specifically for Python 3.12+

set -e  # Exit on error

echo "========================================"
echo "Book Cover OCR v2 - Python 3.12 Install"
echo "========================================"

# Check Python version
echo ""
echo "[1/5] Checking Python version..."
python3 --version

# Critical: Upgrade pip, setuptools, wheel first
echo ""
echo "[2/5] Upgrading pip, setuptools, and wheel..."
python3 -m pip install --upgrade pip setuptools wheel

# Install numpy first (with binary wheel, not from source)
echo ""
echo "[3/5] Installing numpy from binary wheel..."
pip install numpy==1.26.4

# Install PyTorch (CPU version) - use binary wheels
echo ""
echo "[4/5] Installing PyTorch (this takes 5-10 minutes)..."
pip install torch==2.2.1 torchvision==0.17.1 --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
echo ""
echo "[5/5] Installing remaining dependencies..."
pip install -r requirements_py312.txt

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "
import numpy as np
import torch
import transformers
import faiss
import fastapi
import cv2
print('✓ All critical packages imported successfully!')
print(f'  - NumPy: {np.__version__}')
print(f'  - PyTorch: {torch.__version__}')
print(f'  - Transformers: {transformers.__version__}')
print(f'  - FAISS: {faiss.__version__}')
print(f'  - FastAPI: {fastapi.__version__}')
"

# Setup application
echo ""
echo "Setting up application..."
if [ -f "meta.json" ]; then
    echo "Found existing meta.json, running migration..."
    python3 migrate_to_v2.py || echo "Migration skipped (will run later)"
else
    echo "Initializing fresh database..."
    python3 -c "from utils.database import initialize_database; initialize_database()" || echo "Database init skipped"
fi

# Replace old app
if [ -f "app.py" ] && [ ! -f "app_v1_backup.py" ]; then
    echo "Backing up v1 app.py..."
    mv app.py app_v1_backup.py
fi

if [ -f "app_v2.py" ]; then
    echo "Installing v2 app..."
    cp app_v2.py app.py
fi

echo ""
echo "========================================"
echo "✓ Installation Complete!"
echo "========================================"
echo ""
echo "To start the service:"
echo "  uvicorn app:app --host 0.0.0.0 --port 8000"
echo ""
echo "Web interface: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo ""
echo "Next steps:"
echo "  1. Run: python3 test_v2.py"
echo "  2. Start service: uvicorn app:app --host 0.0.0.0 --port 8000"
echo "========================================"

