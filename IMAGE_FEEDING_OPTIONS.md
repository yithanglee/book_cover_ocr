# 📸 Image Feeding Options - Complete Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        GMKtec M3 (8GB RAM)                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Book Cover OCR Service                     │ │
│  │              FastAPI + MobileNet + FAISS                    │ │
│  │                   Port: 8000                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ▲                                   │
│                              │                                   │
│                    Multiple Input Methods                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼────┐            ┌────▼────┐           ┌────▼────┐
   │  Web UI │            │   API   │           │  Folder │
   │ Browser │            │  HTTP   │           │ Watcher │
   └─────────┘            └─────────┘           └─────────┘
```

---

## Method 1: Web Browser Interface 🌐

### Overview
Beautiful drag-and-drop web interface accessible from any browser.

### Setup
```bash
# Start service
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Access Points
- **Local**: http://localhost:8000
- **Network**: http://192.168.1.100:8000 (use your GMKtec IP)

### Device Support
```
┌─────────────────┐
│  Desktop PC     │ ──┐
│  (Windows/Mac)  │   │
└─────────────────┘   │
                      │
┌─────────────────┐   │    ┌──────────────────┐
│  Laptop         │ ──┼───→│   GMKtec M3      │
│  (Linux/Any)    │   │    │  Book OCR Service│
└─────────────────┘   │    └──────────────────┘
                      │
┌─────────────────┐   │
│  Mobile Phone   │ ──┘
│  (iOS/Android)  │
└─────────────────┘
```

### Features
- ✅ Drag & drop images
- ✅ Click to upload
- ✅ Live preview
- ✅ Real-time results
- ✅ No installation needed on client
- ✅ Works on any device with browser

### Best For
- 👤 Individual book scanning
- 🧪 Testing and demos
- 📱 Mobile device access
- 🏢 Public kiosks

---

## Method 2: HTTP API Integration 🔌

### Overview
RESTful API for programmatic access from any programming language.

### Endpoints

#### POST /recognize (Multipart)
```bash
curl -X POST "http://192.168.1.100:8000/recognize" \
  -F "file=@book_cover.jpg"
```

#### POST /recognize_base64 (JSON)
```bash
curl -X POST "http://192.168.1.100:8000/recognize_base64" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_image_here"}'
```

### Language Examples

**Python:**
```python
import requests

with open("cover.jpg", "rb") as f:
    response = requests.post(
        "http://192.168.1.100:8000/recognize",
        files={"file": f}
    )
print(response.json())
```

**JavaScript/Node.js:**
```javascript
const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('file', fs.createReadStream('cover.jpg'));

fetch('http://192.168.1.100:8000/recognize', {
    method: 'POST',
    body: form
})
.then(res => res.json())
.then(data => console.log(data));
```

**PowerShell (Windows):**
```powershell
$Uri = "http://192.168.1.100:8000/recognize"
$FilePath = "C:\book_cover.jpg"
Invoke-RestMethod -Uri $Uri -Method Post -Form @{
    file = Get-Item -Path $FilePath
}
```

**Bash:**
```bash
curl -X POST "http://192.168.1.100:8000/recognize" \
  -F "file=@/path/to/book.jpg"
```

### Best For
- 🔧 Custom applications
- 🤖 Automation scripts
- 🌐 Web services integration
- 📱 Mobile app backends
- 🖥️ Desktop applications

---

## Method 3: Batch Processing 📦

### Overview
Process multiple images in parallel from a directory.

### Usage
```bash
python batch_process.py /path/to/images/ results.json
```

### Workflow
```
Directory with Images                    JSON Results
┌─────────────────┐                    ┌─────────────────┐
│  book1.jpg      │ ──┐                │  {              │
│  book2.jpg      │   │                │    "file": "...",│
│  book3.png      │   ├──→ Process ──→ │    "result": ..│
│  book4.jpg      │   │   (parallel)   │  }              │
│  ...            │ ──┘                │  ...            │
└─────────────────┘                    └─────────────────┘
```

### Configuration
```python
# Edit batch_process.py
MAX_WORKERS = 4  # Adjust for your RAM (2-4 for 8GB)
```

### Example Output
```
Found 25 images to process
Processing with 4 workers...

[1/25] ✓ book_001.jpg
    Top match: B001 (distance: 0.1234)

[2/25] ✓ book_002.jpg
    Top match: B003 (distance: 0.2456)

...

Summary: 25/25 images processed successfully
```

### Best For
- 📚 Large library cataloging
- 🗂️ Archive digitization
- 🏢 Bulk processing tasks
- 💾 Offline processing
- 📊 Batch reporting

---

## Method 4: Folder Watcher (Auto-Process) 👁️

### Overview
Automatically process images as they appear in a watched folder.

### Usage
```bash
python watch_folder.py /watch/folder/ /results/folder/
```

### Workflow
```
Watched Folder          Book OCR Service        Results Folder
┌──────────────┐        ┌──────────────┐       ┌──────────────┐
│              │        │              │       │              │
│  [New File]  │ ────→  │  Processing  │ ────→ │  Result JSON │
│  book.jpg    │        │              │       │  book.json   │
│              │        │              │       │              │
└──────────────┘        └──────────────┘       └──────────────┘
    Monitors                Automatic             Saves results
```

### Integration Scenarios

#### Scenario 1: Scanner Integration
```
Scanner Output           Watch Folder          OCR Service
┌──────────────┐        ┌──────────────┐      ┌──────────────┐
│              │        │              │      │              │
│  Scan book   │──scan──→│  Receives   │──→   │  Recognizes  │
│  cover       │        │  image       │      │  book        │
│              │        │              │      │              │
└──────────────┘        └──────────────┘      └──────────────┘
```

#### Scenario 2: Network Share
```
Remote PC               Network Share          GMKtec M3
┌──────────────┐       ┌──────────────┐      ┌──────────────┐
│ Drop image   │──SMB──→│ Shared       │──→   │ Watches &    │
│ to share     │       │ folder       │      │ processes    │
└──────────────┘       └──────────────┘      └──────────────┘
```

#### Scenario 3: Camera/Mobile Upload
```
Mobile Device          FTP/SFTP Server        Watch Folder
┌──────────────┐       ┌──────────────┐      ┌──────────────┐
│ Take photo   │──→    │ Receives     │──→   │ Auto-process │
│ Upload via   │       │ uploads      │      │              │
│ FTP app      │       │              │      │              │
└──────────────┘       └──────────────┘      └──────────────┘
```

### Setup Network Share (Samba)
```bash
# Install Samba
sudo apt install samba -y

# Create shared folder
mkdir -p ~/book_processing/incoming
mkdir -p ~/book_processing/results

# Configure Samba (/etc/samba/smb.conf)
[BookOCR]
path = /home/user/book_processing/incoming
browseable = yes
writable = yes

# Start watcher
python watch_folder.py ~/book_processing/incoming \
                       ~/book_processing/results

# Access from Windows: \\gmktec-ip\BookOCR
```

### Best For
- 🖨️ Scanner integration
- 🌐 Network share workflows
- 🤖 Automated pipelines
- 📸 Camera uploads
- 🔄 Continuous processing

---

## Comparison Matrix

| Feature | Web UI | API | Batch | Watcher |
|---------|--------|-----|-------|---------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Speed** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Automation** | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Mobile Support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ |
| **Bulk Processing** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Integration** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Setup Complexity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## Real-World Use Cases

### 📚 Use Case 1: Personal Library
**Goal**: Catalog your home book collection

**Solution**: Web UI + Mobile
```
1. Place GMKtec M3 in your library
2. Start service: uvicorn app:app --host 0.0.0.0 --port 8000
3. Use mobile browser: http://gmktec-ip:8000
4. Take photos of book covers and upload
5. Get instant recognition
```

### 🏢 Use Case 2: Library/Bookstore
**Goal**: Rapid book check-in and cataloging

**Solution**: Scanner + Folder Watcher
```
1. Connect scanner to network
2. Configure scanner to save to watched folder
3. Run: python watch_folder.py ~/scanner_output/ ~/catalog/
4. Scan books → Automatic recognition
5. Results saved as JSON for import into catalog system
```

### 🏫 Use Case 3: Book Donation Center
**Goal**: Process large volumes quickly

**Solution**: Batch Processing
```
1. Photograph book covers throughout the day
2. Transfer photos to GMKtec M3
3. Run: python batch_process.py ~/photos/ results.json
4. Import results.json into inventory system
```

### 🏠 Use Case 4: Multi-User Environment
**Goal**: Multiple people scanning from different locations

**Solution**: Network Share + Watcher
```
1. Set up Samba share on GMKtec M3
2. Run folder watcher on shared directory
3. Users drop images from their PCs into share
4. Automatic processing
5. Results available in shared results folder
```

### 📱 Use Case 5: Mobile App Integration
**Goal**: Custom mobile app for book recognition

**Solution**: HTTP API
```
1. Mobile app captures book cover photo
2. Encodes to base64 or multipart
3. POSTs to http://gmktec-ip:8000/recognize
4. Receives JSON response
5. Displays results in app
```

---

## Network Topology Examples

### Simple Home Network
```
┌─────────────┐     WiFi      ┌─────────────┐
│   Router    │◄──────────────►│   Laptop    │
│192.168.1.1  │                └─────────────┘
└──────┬──────┘                        │
       │                               │
       │ Ethernet                      │ HTTP
       │                               ▼
┌──────▼──────┐                ┌─────────────┐
│  GMKtec M3  │                │  Access     │
│192.168.1.100│                │  Service    │
│  Port 8000  │◄───────────────┤  via        │
└─────────────┘   HTTP         │  Browser    │
                                └─────────────┘
```

### Office Network with Share
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   PC #1     │      │   PC #2     │      │   PC #3     │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │        SMB Share   │                    │
       └────────────┬───────┴────────────────────┘
                    │
              ┌─────▼──────┐
              │  GMKtec M3 │
              │  Watched:  │
              │  ~/shared  │
              └────────────┘
```

---

## Performance Guidelines

### For GMKtec M3 (8GB RAM)

| Method | Recommended Settings | Throughput |
|--------|---------------------|------------|
| **Web UI** | 2 workers | 2-4 requests/sec |
| **API** | 2 workers | 2-4 requests/sec |
| **Batch** | 2-4 parallel | 10-20 images/min |
| **Watcher** | Single process | 10-15 images/min |

### Memory Usage
- **Base service**: ~500MB
- **Per worker**: ~200-300MB
- **Per image processing**: ~50MB temporary

### Optimization Tips
1. **Use batch processing** for large collections
2. **Use folder watcher** for continuous workflows
3. **Limit concurrent requests** to avoid OOM
4. **Consider image pre-processing** (resize if very large)
5. **Monitor with htop** during heavy use

---

## Quick Command Reference

```bash
# Start service (basic)
uvicorn app:app --host 0.0.0.0 --port 8000

# Start service (optimized for 8GB RAM)
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2

# Test single image
curl -X POST "http://localhost:8000/recognize" -F "file=@test.jpg"

# Batch process
python batch_process.py ~/images/ results.json

# Watch folder
python watch_folder.py ~/incoming/ ~/results/

# Check health
curl http://localhost:8000/health

# View all books
curl http://localhost:8000/books

# Check memory usage
free -h

# Monitor system
htop
```

---

## Troubleshooting Decision Tree

```
Cannot access service?
├── From local machine?
│   ├── YES → Check if service is running (curl localhost:8000/health)
│   │         If not running, start service
│   └── NO  → Check firewall (sudo ufw status)
│             Open port 8000 if needed
│
Image not recognized?
├── Valid image format? (JPG/PNG)
│   ├── YES → Check image quality
│   │         Try with known good image
│   └── NO  → Convert to supported format
│
Out of memory errors?
├── Reduce workers to 1
├── Process images sequentially
└── Add swap space if needed
```

---

## Summary

### Choose Your Method:

**🌐 Web UI** - Best for:
- Individual use
- Testing
- Mobile access
- No technical knowledge needed

**🔌 API** - Best for:
- Custom applications
- Programmatic access
- Integration with existing systems

**📦 Batch** - Best for:
- Large collections
- One-time processing
- Offline workflows

**👁️ Watcher** - Best for:
- Automated workflows
- Scanner integration
- Continuous processing
- Multiple users

**💡 Pro Tip**: Combine methods! Use the web UI for testing, folder watcher for daily operations, and batch processing for bulk imports.

---

**All methods work simultaneously!** Run the service once, and use any/all methods as needed. 🚀

