#!/bin/bash
# Quick installation script for Book Cover OCR v2

set -e  # Exit on error

echo "========================================"
echo "Book Cover OCR v2 - Installation"
echo "========================================"

# Check Python version
echo ""
echo "[1/5] Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Install dependencies
echo ""
echo "[2/5] Installing dependencies..."
echo "This may take 5-10 minutes (downloading PyTorch and CLIP models)..."
pip install -r requirements.txt

# Run migration if meta.json exists
echo ""
echo "[3/5] Setting up database..."
if [ -f "meta.json" ]; then
    echo "Found existing meta.json, running migration..."
    python3 migrate_to_v2.py
else
    echo "No existing data, initializing fresh database..."
    python3 -c "from utils.database import initialize_database; initialize_database()"
fi

# Replace old app if it exists
echo ""
echo "[4/5] Setting up application..."
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
echo "[5/5] Running tests..."
echo "Starting service for testing..."

# Start service in background
uvicorn app:app --host 0.0.0.0 --port 8000 &
SERVICE_PID=$!

# Wait for service to start
echo "Waiting for service to start..."
sleep 10

# Run tests
echo "Running tests..."
python3 test_v2.py || true

# Stop test service
kill $SERVICE_PID 2>/dev/null || true

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "To start the service:"
echo "  uvicorn app:app --host 0.0.0.0 --port 8000"
echo ""
echo "Or as a background service:"
echo "  sudo cp book-ocr.service /etc/systemd/system/"
echo "  sudo systemctl enable book-ocr"
echo "  sudo systemctl start book-ocr"
echo ""
echo "Web interface: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo "Health check: http://localhost:8000/health"
echo ""
echo "For more information, see UPGRADE_TO_V2.md"
echo "========================================"

