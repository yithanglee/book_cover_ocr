# Deployment Guide for GMKtec M3

Step-by-step guide to deploy the Book Cover OCR service on your GMKtec M3 (8GB RAM).

## 📋 Prerequisites

- GMKtec M3 with 8GB RAM
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8 or higher
- Network connectivity

## 🚀 Installation Steps

### Step 1: System Preparation

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install libgl1-mesa-glx libglib2.0-0 -y
```

### Step 2: Copy Project Files

Transfer the project to your GMKtec M3:

```bash
# Using scp (from your current machine)
scp -r book_cover_ocr/ user@gmktec-ip:/home/user/

# Or using rsync
rsync -av book_cover_ocr/ user@gmktec-ip:/home/user/book_cover_ocr/

# Or use a USB drive
# Copy to USB, then on GMKtec:
cp -r /media/usb/book_cover_ocr /home/user/
```

### Step 3: Install Dependencies

```bash
cd /home/user/book_cover_ocr

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 4: Test the Service

```bash
# Start the service
uvicorn app:app --host 0.0.0.0 --port 8000

# In another terminal, test it
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "books_indexed": 3
}
```

### Step 5: Set Up as System Service (Optional)

For automatic startup on boot:

```bash
# Edit the service file to match your paths
nano book-ocr.service

# Copy to systemd
sudo cp book-ocr.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable book-ocr
sudo systemctl start book-ocr

# Check status
sudo systemctl status book-ocr
```

### Step 6: Configure Firewall

Allow access from network:

```bash
# UFW firewall
sudo ufw allow 8000/tcp

# Or iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

### Step 7: Find GMKtec IP Address

```bash
# Get your IP address
hostname -I
# Or
ip addr show
```

Access from other devices: `http://<GMKtec-IP>:8000`

## 🖥️ Access Methods

### 1. Local Access (on GMKtec)

```bash
# Web interface
firefox http://localhost:8000

# Or using curl
curl -X POST "http://localhost:8000/recognize" \
  -F "file=@test_image.jpg"
```

### 2. Network Access (from other machines)

```bash
# From Windows PC, Mac, or another Linux machine
# Open browser: http://192.168.1.100:8000 (use your GMKtec IP)

# Or using curl
curl -X POST "http://192.168.1.100:8000/recognize" \
  -F "file=@book_cover.jpg"
```

### 3. Mobile Access

- Open mobile browser
- Navigate to: `http://<GMKtec-IP>:8000`
- Use camera to take photo or upload from gallery

## 📁 Folder-Based Workflows

### Setup 1: Shared Network Folder

Create a watched folder accessible from other machines:

```bash
# Install Samba for Windows/Mac sharing
sudo apt install samba -y

# Create shared folder
mkdir -p ~/book_processing/incoming
mkdir -p ~/book_processing/results

# Configure Samba
sudo nano /etc/samba/smb.conf
```

Add to `smb.conf`:
```ini
[BookOCR]
path = /home/user/book_processing/incoming
browseable = yes
writable = yes
guest ok = no
valid users = user
```

Start folder watcher:
```bash
python watch_folder.py ~/book_processing/incoming ~/book_processing/results
```

### Setup 2: USB Scanner Integration

For USB-connected scanners:

```bash
# Install scanner software
sudo apt install sane sane-utils -y

# Create scan-to-folder script
mkdir -p ~/scanner_output

# Watch this folder
python watch_folder.py ~/scanner_output ~/ocr_results
```

## 🔧 Performance Optimization for 8GB RAM

### Memory Management

```bash
# Monitor memory usage
watch -n 1 free -h

# If running low on memory, reduce workers
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1
```

### Swap Configuration (if needed)

```bash
# Create swap file for better stability
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### CPU Optimization

```bash
# Set CPU governor to performance
sudo apt install cpufrequtils -y
sudo cpufreq-set -g performance
```

## 🌐 Network Configuration Options

### Option 1: Static IP (Recommended)

```bash
# Edit netplan configuration
sudo nano /etc/netplan/01-netcfg.yaml
```

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

```bash
sudo netplan apply
```

### Option 2: DHCP with Reservation

Configure your router to always assign the same IP to the GMKtec M3.

### Option 3: Hostname Access

```bash
# Install avahi for .local domain
sudo apt install avahi-daemon -y

# Access via: http://gmktec.local:8000
```

## 🔐 Security Setup

### Basic Authentication (Recommended for production)

Edit `app.py` to add authentication:

```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from secrets import compare_digest

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials):
    correct_username = compare_digest(credentials.username, "admin")
    correct_password = compare_digest(credentials.password, "your_password")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

### HTTPS with Self-Signed Certificate

```bash
# Generate certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Run with HTTPS
uvicorn app:app --host 0.0.0.0 --port 8443 \
  --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

## 📊 Monitoring

### System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor in real-time
htop  # CPU and RAM
iotop  # Disk I/O
nethogs  # Network usage
```

### Service Logs

```bash
# If using systemd
sudo journalctl -u book-ocr -f

# Or check application logs
tail -f /var/log/book-ocr.log
```

### Health Check Script

Create `monitor.sh`:
```bash
#!/bin/bash
while true; do
    status=$(curl -s http://localhost:8000/health | jq -r .status)
    echo "$(date): Service status: $status"
    if [ "$status" != "healthy" ]; then
        echo "Service unhealthy! Restarting..."
        sudo systemctl restart book-ocr
    fi
    sleep 60
done
```

## 🐛 Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u book-ocr -n 50

# Check port availability
sudo lsof -i :8000

# Verify dependencies
pip list | grep -E "fastapi|uvicorn|opencv"
```

### Out of memory errors

```bash
# Check memory usage
free -h

# Reduce workers
# Edit /etc/systemd/system/book-ocr.service
# Change: --workers 1

sudo systemctl daemon-reload
sudo systemctl restart book-ocr
```

### Cannot access from network

```bash
# Check firewall
sudo ufw status

# Check service binding
netstat -tuln | grep 8000

# Test locally first
curl http://localhost:8000/health

# Test from network
curl http://<GMKtec-IP>:8000/health
```

### Model files missing

```bash
# Verify files exist
ls -lh models/mobilenet.onnx
ls -lh embeddings.npy
ls -lh meta.json

# Check file permissions
chmod 644 models/mobilenet.onnx embeddings.npy meta.json
```

## 📱 Client Setup Examples

### Windows PowerShell

```powershell
# Test upload
$Uri = "http://192.168.1.100:8000/recognize"
$FilePath = "C:\Users\User\Desktop\book_cover.jpg"
$Form = @{
    file = Get-Item -Path $FilePath
}
Invoke-RestMethod -Uri $Uri -Method Post -Form $Form
```

### Android (Termux)

```bash
# Install curl
pkg install curl

# Upload image
curl -X POST "http://192.168.1.100:8000/recognize" \
  -F "file=@/sdcard/DCIM/book.jpg"
```

### iOS (Shortcuts App)

Create a shortcut:
1. Get image from Photos/Camera
2. "Get Contents of URL"
   - URL: `http://<GMKtec-IP>:8000/recognize`
   - Method: POST
   - Form: file = [Image]

## 🎯 Production Checklist

- [ ] System dependencies installed
- [ ] Python environment set up
- [ ] Service starts without errors
- [ ] Health check returns "healthy"
- [ ] Accessible from network
- [ ] Firewall configured
- [ ] Systemd service enabled
- [ ] Authentication configured (if needed)
- [ ] Monitoring set up
- [ ] Backup strategy planned
- [ ] Documentation accessible

## 📈 Performance Benchmarks (GMKtec M3, 8GB RAM)

Expected performance:
- **Single image**: 50-200ms
- **Concurrent requests**: 2-4 requests/second
- **Batch processing**: 10-20 images/minute
- **Memory usage**: 500MB-1GB per worker
- **Startup time**: 2-5 seconds

## 🔄 Backup and Updates

### Backup Important Files

```bash
# Backup embeddings and metadata
tar -czf backup-$(date +%Y%m%d).tar.gz \
  embeddings.npy meta.json models/
```

### Update Service

```bash
# Pull latest code
git pull  # or copy updated files

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart book-ocr
```

---

**Your Book Cover OCR service is now ready to use on GMKtec M3!** 🎉

For support, check logs and monitor system resources.

