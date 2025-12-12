#!/bin/bash
# Quick fix for Python 3.12 distutils issue

echo "Fixing Python 3.12 distutils issue..."
echo ""

# Step 1: Upgrade pip, setuptools, and wheel
echo "[1/3] Upgrading pip, setuptools, and wheel..."
python3 -m pip install --upgrade pip setuptools wheel

# Step 2: Install dependencies one by one (more reliable)
echo ""
echo "[2/3] Installing dependencies..."
echo "This will take 5-10 minutes..."

# Install in order of dependencies
pip install numpy==1.24.3
pip install Pillow==10.2.0
pip install requests==2.31.0
pip install cachetools==5.3.2
pip install tqdm==4.66.1
pip install aiosqlite==0.19.0
pip install watchdog==3.0.0
pip install python-multipart==0.0.6

# Install PyTorch (CPU version)
pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cpu

# Install transformers and related
pip install transformers==4.36.2

# Install FastAPI stack
pip install fastapi==0.109.0
pip install uvicorn[standard]==0.27.0

# Install CV and ML libraries
pip install opencv-python-headless==4.9.0.80
pip install onnxruntime==1.16.3
pip install faiss-cpu==1.7.4

echo ""
echo "[3/3] Verifying installation..."
python3 -c "import torch; import transformers; import faiss; import fastapi; print('✓ All packages imported successfully!')"

echo ""
echo "========================================"
echo "✓ Installation fixed!"
echo "========================================"
echo ""
echo "You can now run:"
echo "  python3 migrate_to_v2.py"
echo "  uvicorn app:app --host 0.0.0.0 --port 8000"

