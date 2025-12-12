# Book Cover OCR Service

On-premises OCR service for recognizing books from cover images using MobileNet embeddings and FAISS similarity search.

## 🖥️ System Requirements

- **Tested on**: GMKtec M3, 8GB RAM
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8+
- **Disk Space**: ~500MB for dependencies

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or copy the project to your GMKtec M3
cd /path/to/book_cover_ocr

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Start the Service

```bash
# Start the FastAPI server
uvicorn app:app --host 0.0.0.0 --port 8000

# For production (with auto-reload disabled)
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
```

The service will be available at:
- **Web Interface**: http://localhost:8000
- **API**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

### 3. Access from Other Machines

To access from other devices on your network:
```
http://<GMKtec-IP>:8000
```

Find your IP with: `ip addr show` or `hostname -I`

## 📸 Ways to Feed Images

### Method 1: Web Interface (Easiest)

1. Open browser: `http://localhost:8000`
2. Drag & drop or click to upload image
3. View results instantly

**Features:**
- ✅ Beautiful, modern UI
- ✅ Drag & drop support
- ✅ Live preview
- ✅ Real-time results

### Method 2: HTTP API

#### Using curl:
```bash
curl -X POST "http://localhost:8000/recognize" \
  -F "file=@/path/to/book_cover.jpg"
```

#### Using Python:
```python
import requests

with open("book_cover.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/recognize",
        files={"file": f}
    )
    print(response.json())
```

#### Using base64 (useful for embedded systems):
```python
import requests
import base64

with open("book_cover.jpg", "rb") as f:
    img_data = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:8000/recognize_base64",
    json={"image": img_data}
)
print(response.json())
```

### Method 3: Batch Processing

Process multiple images from a directory:

```bash
python batch_process.py /path/to/images/ results.json
```

**Features:**
- ✅ Parallel processing (4 workers by default)
- ✅ Progress tracking
- ✅ JSON output
- ✅ Error handling

**Example:**
```bash
# Process all images in a folder
python batch_process.py ~/book_covers/ output.json

# Results saved to output.json
```

### Method 4: Folder Watcher (Automatic)

Automatically process images when they're added to a folder:

```bash
python watch_folder.py /path/to/watch/ /path/to/results/
```

**Features:**
- ✅ Real-time monitoring
- ✅ Automatic processing
- ✅ Results saved as JSON
- ✅ Perfect for scanner workflows

**Use Cases:**
- Drop images from scanner
- Network share monitoring
- Automated workflows

**Example:**
```bash
# Watch a folder and save results
python watch_folder.py ~/incoming_books/ ~/results/

# Now just drop images into ~/incoming_books/
```

## 🌐 Network Setup Options

### Option 1: Direct Network Access

Make the service accessible from other machines:

```bash
# Start with network binding
uvicorn app:app --host 0.0.0.0 --port 8000
```

Access from any device: `http://<GMKtec-IP>:8000`

### Option 2: Network Share

Share a folder for image drop-off:

```bash
# Create shared folder
mkdir -p ~/shared_books

# Start folder watcher
python watch_folder.py ~/shared_books/ ~/results/
```

Then mount `~/shared_books` as a network share (SMB/NFS).

### Option 3: Reverse Proxy (Production)

For production deployment with nginx:

```nginx
server {
    listen 80;
    server_name bookocr.local;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Configuration

### Adjust Workers for 8GB RAM

For GMKtec M3 with 8GB RAM, use 2-4 workers:

```bash
# Recommended for 8GB RAM
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
```

### Batch Processing Workers

Edit `batch_process.py`:
```python
MAX_WORKERS = 2  # Adjust based on available RAM
```

## 📊 API Response Format

```json
{
  "candidates": ["B001", "B002", "B003", "B004", "B005"],
  "distance": [0.1234, 0.2345, 0.3456, 0.4567, 0.5678]
}
```

- **candidates**: Top 5 matching book IDs (ranked)
- **distance**: Similarity distances (lower = better match)

## 🔍 Monitoring

### Check Service Health
```bash
curl http://localhost:8000/health
```

### View All Books
```bash
curl http://localhost:8000/books
```

### Check Logs
```bash
# If running with systemd
journalctl -u book-ocr -f
```

## 🐳 Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Run:
```bash
docker build -t book-ocr .
docker run -p 8000:8000 book-ocr
```

## 🔐 Security Notes

For production deployment:
1. Add authentication (API keys)
2. Use HTTPS with SSL certificates
3. Implement rate limiting
4. Restrict CORS origins
5. Run as non-root user

## 🛠️ Troubleshooting

### Service won't start
```bash
# Check if port is in use
sudo lsof -i :8000

# Kill existing process
sudo kill -9 <PID>
```

### Out of memory
```bash
# Reduce workers
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1

# Check memory usage
free -h
```

### Image upload fails
- Check file size limits (default: 10MB in FastAPI)
- Verify image format (JPG, PNG, etc.)
- Check network connectivity

## 📈 Performance Tips

For GMKtec M3 (8GB RAM):
1. Use 2 workers max
2. Process images at 224x224 (already configured)
3. Batch processing: 2-4 parallel workers
4. Consider SSD for embeddings storage
5. Monitor RAM usage: `htop` or `free -h`

## 📝 File Structure

```
book_cover_ocr/
├── app.py                  # Main FastAPI application
├── batch_process.py        # Batch processing script
├── watch_folder.py         # Folder monitoring script
├── requirements.txt        # Python dependencies
├── embeddings.npy          # Pre-computed embeddings
├── meta.json               # Book metadata
├── models/
│   └── mobilenet.onnx      # MobileNet model
├── utils/
│   └── embedding.py        # Embedding utilities
└── static/
    └── index.html          # Web interface
```

## 🎯 Use Cases

1. **Library Management**: Scan books and auto-catalog
2. **Personal Library**: Organize your collection
3. **Bookstore**: Quick inventory lookup
4. **Book Donation Centers**: Fast sorting
5. **Academic Libraries**: Research material tracking

## 📞 Support

For issues or questions, check:
- `/health` endpoint for service status
- Application logs
- System resources: `htop`

---

**Optimized for GMKtec M3 with 8GB RAM** 🚀

