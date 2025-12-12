# 🔧 Setup Instructions - First Time Setup

## Your Current Issue

The `embeddings.npy` file is empty because you haven't added book cover images yet!

## 📋 Step-by-Step Setup

### Step 1: Create Directory Structure

```bash
cd /data/bookcv
mkdir -p covers
```

### Step 2: Add Your Book Cover Images

Place your book cover images in the `covers/` directory:

```bash
# Example:
covers/
├── book_001.jpg
├── book_002.jpg
├── book_003.jpg
└── ...
```

**Image Requirements:**
- ✅ Format: JPG, PNG, JPEG
- ✅ Quality: Clear, well-lit book covers
- ✅ Size: Any size (will be resized to 224x224 automatically)
- ✅ Naming: Use unique IDs (e.g., B001.jpg, B002.jpg, or any name)

### Step 3: Update `meta.json`

Edit `meta.json` to match your books:

```json
{
  "B001": {
    "title": "Your First Book Title",
    "author": "Author Name",
    "image": "covers/B001.jpg"
  },
  "B002": {
    "title": "Your Second Book Title",
    "author": "Author Name",
    "image": "covers/B002.jpg"
  }
}
```

**Important:** The book IDs (B001, B002, etc.) and image paths must match your actual files!

### Step 4: Generate Embeddings

```bash
python3 generate_embeddings.py
```

You should see:
```
Generated embeddings for X books → /data/bookcv/embeddings.npy
```

### Step 5: Start the Service

```bash
# Since you have cloudflared on port 8000, use port 8001
uvicorn app:app --host 0.0.0.0 --port 8001
```

### Step 6: Access via Cloudflare Tunnel

Your service will be accessible via your cloudflare tunnel!

---

## 🎯 Quick Start for Testing (No Books Yet)

If you want to test the system first without real books, I'll create a demo mode for you.

---

## ❓ FAQ

### Q: I don't have book cover images yet, can I still test?
**A:** Yes! Use the demo mode script I'll create. It will generate sample data.

### Q: How many books can I add?
**A:** As many as you want! Limited only by disk space and RAM. For 8GB RAM, thousands of books is fine.

### Q: Can I add more books later?
**A:** Yes! Just:
1. Add new images to `covers/`
2. Update `meta.json`
3. Re-run `generate_embeddings.py`
4. Restart the service

### Q: What if my images are named differently?
**A:** No problem! Just make sure the paths in `meta.json` match your actual files.

---

## 🚨 Common Errors

### Error: `EOFError: No data left in file`
**Cause:** `embeddings.npy` is empty (no embeddings generated)
**Solution:** Follow Step 2-4 above

### Error: `Cannot read image: /path/to/image.jpg`
**Cause:** Image file doesn't exist at specified path
**Solution:** 
- Check file path in `meta.json`
- Verify image exists: `ls -la covers/`
- Check image is readable: `file covers/B001.jpg`

### Error: `Aborted!` when starting uvicorn
**Cause:** Usually port conflict or missing embeddings
**Solution:**
- Try different port: `--port 8001`
- Check embeddings exist: `ls -lh embeddings.npy`
- If size is 0 bytes, regenerate embeddings

---

## 📊 Checking Your Setup

Run this to check your setup:

```bash
# Check directory structure
ls -la

# Check covers directory
ls -la covers/

# Check embeddings file size
ls -lh embeddings.npy

# Check meta.json
cat meta.json

# Check if port is available
lsof -i :8001
```

---

## 🎨 Example Workflow

### Scenario: Setting up a small library

```bash
# 1. Take photos of 10 book covers with your phone
# 2. Transfer to computer

# 3. Copy to GMKtec M3
scp *.jpg scmc@scmc-M3:/data/bookcv/covers/

# 4. SSH into GMKtec M3
ssh scmc@scmc-M3

# 5. Go to project
cd /data/bookcv

# 6. Create/update meta.json with your books
nano meta.json

# 7. Generate embeddings
python3 generate_embeddings.py

# 8. Start service
uvicorn app:app --host 0.0.0.0 --port 8001

# 9. Access via cloudflare tunnel
# Open your cloudflare URL in browser
```

---

## 🔄 Next Steps

1. **Get some book cover images** (photo, download, scan)
2. **Place them in `covers/` directory**
3. **Update `meta.json`** with your book info
4. **Generate embeddings**
5. **Start the service**
6. **Start recognizing books!**

---

Need a demo setup? I'll create a script that generates sample data for testing!

