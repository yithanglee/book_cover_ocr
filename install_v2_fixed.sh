#!/bin/bash
# Fixed installation script for Book Cover OCR v2 (Python 3.12 compatible)

set -e  # Exit on error

echo "========================================"
echo "Book Cover OCR v2 - Installation (Fixed)"
echo "========================================"

# Check Python version
echo ""
echo "[1/6] Checking Python version..."
python3 --version

# Upgrade pip, setuptools, and wheel FIRST (critical for Python 3.12)
echo ""
echo "[2/6] Upgrading pip, setuptools, and wheel..."
echo "This fixes distutils issues in Python 3.12..."
python3 -m pip install --upgrade pip setuptools wheel

# Install dependencies in stages to avoid conflicts
echo ""
echo "[3/6] Installing core dependencies..."
pip install numpy==1.24.3

echo ""
echo "[4/6] Installing PyTorch and vision libraries..."
echo "This may take 5-10 minutes..."
pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cpu

echo ""
echo "[5/6] Installing remaining dependencies..."
pip install fastapi==0.109.0
pip install uvicorn[standard]==0.27.0
pip install python-multipart==0.0.6
pip install opencv-python-headless==4.9.0.80
pip install onnxruntime==1.16.3
pip install faiss-cpu==1.7.4
pip install requests==2.31.0
pip install watchdog==3.0.0
pip install transformers==4.36.2
pip install Pillow==10.2.0
pip install aiosqlite==0.19.0
pip install cachetools==5.3.2
pip install tqdm==4.66.1

echo ""
echo "[6/6] Setting up database and application..."
if [ -f "meta.json" ]; then
    echo "Found existing meta.json, running migration..."
    python3 migrate_to_v2.py || echo "Migration step skipped"
else
    echo "No existing data, initializing fresh database..."
    python3 -c "from utils.database import initialize_database; initialize_database()" || echo "Database init skipped"
fi

# Replace old app if it exists
if [ -f "app.py" ] && [ ! -f "app_v1_backup.py" ]; then
    echo "Backing up v1 app.py..."
    mv app.py app_v1_backup.py
fi

if [ -f "app_v2.py" ]; then
    echo "Installing v2 app..."
    cp app_v2.py app.py
fi

# Make scripts executable
chmod +x migrate_to_v2.py 2>/dev/null || true
chmod +x generate_embeddings_v2.py 2>/dev/null || true
chmod +x test_v2.py 2>/dev/null || true

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "To start the service:"
echo "  uvicorn app:app --host 0.0.0.0 --port 8000"
echo ""
echo "Web interface: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo ""
echo "For more information, see UPGRADE_TO_V2.md"
echo "========================================"

