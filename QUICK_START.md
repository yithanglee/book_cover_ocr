# 🚀 Quick Start - Book Cover OCR

## For GMKtec M3 (8GB RAM)

### ⚡ Super Quick Start (5 minutes)

```bash
# 1. Run setup script
chmod +x setup.sh
./setup.sh

# 2. Start service
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000

# 3. Open browser
# Visit: http://localhost:8000
```

**That's it!** Drag and drop book cover images to recognize them.

---

## 📸 4 Ways to Feed Images

### 1️⃣ Web Interface (Easiest)
```bash
# Open in browser
http://localhost:8000
```
- ✅ Beautiful UI
- ✅ Drag & drop
- ✅ Real-time results
- 🎯 **Best for**: Manual scanning, testing

### 2️⃣ HTTP API
```bash
curl -X POST "http://localhost:8000/recognize" \
  -F "file=@book_cover.jpg"
```
- ✅ Simple integration
- ✅ Language-agnostic
- 🎯 **Best for**: Integration with other apps

### 3️⃣ Batch Processing
```bash
python batch_process.py /path/to/images/ results.json
```
- ✅ Process multiple images
- ✅ Parallel processing
- ✅ JSON output
- 🎯 **Best for**: Processing large collections

### 4️⃣ Folder Watcher (Auto-process)
```bash
python watch_folder.py /path/to/watch/ /path/to/results/
```
- ✅ Automatic processing
- ✅ Real-time monitoring
- ✅ Zero manual intervention
- 🎯 **Best for**: Scanner integration, automated workflows

---

## 🌐 Access from Network

### Find Your IP
```bash
hostname -I
```

### Access from Any Device
```
http://<YOUR-IP>:8000
```

Works on:
- ✅ Windows PC
- ✅ Mac
- ✅ Linux
- ✅ Android/iOS (browser)
- ✅ Any device on same network

---

## 💡 Common Use Cases

### Use Case 1: Library Cataloging
```bash
# Start service
uvicorn app:app --host 0.0.0.0 --port 8000

# Use web interface or batch process
python batch_process.py ~/library_photos/ catalog.json
```

### Use Case 2: Scanner Integration
```bash
# Watch scanner output folder
python watch_folder.py ~/scanner_output/ ~/results/

# Configure scanner to save to ~/scanner_output/
# Books automatically recognized!
```

### Use Case 3: Network Share
```bash
# Create shared folder
mkdir -p ~/shared_books

# Start watcher
python watch_folder.py ~/shared_books/ ~/results/

# Share ~/shared_books via Samba/NFS
# Drop images from any computer → automatic recognition!
```

### Use Case 4: Mobile App Integration
```python
# In your mobile app, POST to:
http://<GMKtec-IP>:8000/recognize

# Or use base64 endpoint:
http://<GMKtec-IP>:8000/recognize_base64
```

---

## 🔧 Configuration Tips

### For 8GB RAM (Recommended)
```bash
# 2 workers for optimal performance
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
```

### For Lower Memory
```bash
# 1 worker to save RAM
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1
```

### Run as Background Service
```bash
# Copy service file
sudo cp book-ocr.service /etc/systemd/system/

# Edit paths in service file if needed
sudo nano /etc/systemd/system/book-ocr.service

# Enable and start
sudo systemctl enable book-ocr
sudo systemctl start book-ocr

# Check status
sudo systemctl status book-ocr
```

---

## 📊 API Response Example

```json
{
  "candidates": ["B001", "B002", "B003", "B004", "B005"],
  "distance": [0.1234, 0.2345, 0.3456, 0.4567, 0.5678]
}
```

**Lower distance = Better match!**

---

## 🐛 Troubleshooting

### Can't start service
```bash
# Check if port is in use
sudo lsof -i :8000

# Kill existing process
sudo kill -9 <PID>
```

### Out of memory
```bash
# Reduce workers to 1
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1

# Check memory
free -h
```

### Can't access from network
```bash
# Open firewall
sudo ufw allow 8000/tcp

# Verify service is listening on all interfaces
netstat -tuln | grep 8000
```

---

## 📚 More Information

- **README.md** - Complete feature documentation
- **DEPLOYMENT.md** - Detailed deployment guide
- **client_example.py** - Python client examples

---

## ⚡ One-Liner Commands

```bash
# Install and start
./setup.sh && source venv/bin/activate && uvicorn app:app --host 0.0.0.0 --port 8000

# Test single image
curl -X POST "http://localhost:8000/recognize" -F "file=@test.jpg"

# Process folder
python batch_process.py ~/books/ results.json

# Watch folder
python watch_folder.py ~/incoming/ ~/results/

# Check health
curl http://localhost:8000/health
```

---

**Ready to recognize books! 📚🚀**

For questions or issues, check the logs and system resources.

