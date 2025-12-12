# 🚀 First Time Setup - Quick Guide

## Your Current Situation

You have:
- ✅ Cloudflared tunnel on port 8000
- ✅ Virtual environment activated
- ❌ Empty `embeddings.npy` file
- ❌ No book cover images yet

---

## 🎯 Solution: Two Options

### Option 1: Quick Demo (2 minutes) - Test First! ✨

```bash
cd /data/bookcv

# Create demo data
python3 create_demo_data.py

# Start service on port 8001
uvicorn app:app --host 0.0.0.0 --port 8001
```

**What this does:**
- Creates 3 demo book covers (colored rectangles)
- Generates embeddings
- Ready to test the web interface!

**Access:** Via your cloudflare tunnel or `http://localhost:8001`

---

### Option 2: Add Your Real Books (10 minutes) 📚

#### Step 1: Verify Current Setup
```bash
cd /data/bookcv
python3 verify_setup.py
```

This will show what's missing.

#### Step 2: Add Your Book Covers
```bash
# Create covers directory
mkdir -p covers

# Copy your book cover images
# Example: Using scp from another machine
# scp *.jpg scmc@scmc-M3:/data/bookcv/covers/

# Or copy from USB
# cp /media/usb/*.jpg covers/

# Or take photos with phone and transfer
```

#### Step 3: Update meta.json
```bash
nano meta.json
```

Example format:
```json
{
  "B001": {
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "image": "covers/great_gatsby.jpg"
  },
  "B002": {
    "title": "1984",
    "author": "George Orwell",
    "image": "covers/1984.jpg"
  }
}
```

**Important:** 
- Book IDs (B001, B002) can be anything unique
- Image paths must match your actual files!

#### Step 4: Generate Embeddings
```bash
python3 generate_embeddings.py
```

Should output: `Generated embeddings for X books`

#### Step 5: Start Service
```bash
# Port 8001 since cloudflared is on 8000
uvicorn app:app --host 0.0.0.0 --port 8001
```

---

## 🔍 If You Get Errors

### Error: "Cannot read image: /data/bookcv/covers/XXX.jpg"

**Solution:**
```bash
# Check if file exists
ls -la covers/

# Check image is readable
file covers/your_image.jpg

# Make sure meta.json path matches actual file
```

### Error: "EOFError: No data left in file"

**Solution:** Your embeddings.npy is empty
```bash
# Quick fix - use demo data
python3 create_demo_data.py

# Then start service
```

### Error: "Aborted!" when starting uvicorn

**Solution:** Check embeddings file size
```bash
# Check file size
ls -lh embeddings.npy

# If 0 bytes or 128 bytes (header only), regenerate
python3 create_demo_data.py
# OR
python3 generate_embeddings.py
```

---

## 📋 Quick Command Reference

```bash
# 1. Verify setup
python3 verify_setup.py

# 2a. Create demo data (for testing)
python3 create_demo_data.py

# 2b. OR generate from your books
python3 generate_embeddings.py

# 3. Start service
uvicorn app:app --host 0.0.0.0 --port 8001

# 4. Test in another terminal
curl http://localhost:8001/health

# 5. Update cloudflare tunnel if needed
# (Point to port 8001 instead of 8000)
```

---

## 🌐 Accessing Your Service

### Local Access
```bash
http://localhost:8001
```

### Via Cloudflare Tunnel
Your existing cloudflare tunnel URL

**Note:** If your tunnel points to port 8000, you have 2 options:
1. Change tunnel to point to 8001
2. Change service to run on 8000 (stop cloudflared first)

---

## ✅ Checklist

Before starting the service:

- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] Dependencies installed: `pip list | grep fastapi`
- [ ] Covers directory exists: `ls covers/`
- [ ] meta.json is valid: `cat meta.json`
- [ ] Embeddings generated: `ls -lh embeddings.npy` (should be > 1KB)
- [ ] Model exists: `ls models/mobilenet.onnx`

---

## 🎯 Recommended: Start with Demo Data

**For your first run, I recommend:**

```bash
# 1. Create demo data
python3 create_demo_data.py

# 2. Start service
uvicorn app:app --host 0.0.0.0 --port 8001

# 3. Open browser to your cloudflare URL
# Upload any image and see it recognize the demo books

# 4. Once working, replace with real books later
```

This way you can:
- ✅ Test that everything works
- ✅ See how the system behaves
- ✅ Understand the workflow
- ✅ Then add real books with confidence

---

## 📞 Need Help?

```bash
# Check system status
python3 verify_setup.py

# Check service health
curl http://localhost:8001/health

# View service logs
# (If running in terminal, you'll see logs directly)

# Check embeddings info
python3 -c "import numpy as np; arr = np.load('embeddings.npy'); print(f'Shape: {arr.shape}, Size: {arr.nbytes} bytes')"
```

---

## 🔄 Common Workflow

```
First Time:
1. create_demo_data.py
2. uvicorn app:app --host 0.0.0.0 --port 8001
3. Test via browser
4. Add real books when ready

Adding Real Books:
1. Add images to covers/
2. Update meta.json
3. python3 generate_embeddings.py
4. Restart service
5. Done!

Adding More Books Later:
1. Add new images to covers/
2. Add entries to meta.json
3. python3 generate_embeddings.py (regenerates ALL)
4. Restart service
```

---

## 🚀 Next Step

Run this now:

```bash
cd /data/bookcv
python3 create_demo_data.py
uvicorn app:app --host 0.0.0.0 --port 8001
```

Then open your cloudflare URL in a browser! 🎉

