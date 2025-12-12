# 📚 How to Add Books for High Confidence Recognition

## 🎯 The Concept

**How it works:**
1. You provide **reference book cover images** (your library)
2. System generates **embeddings** (fingerprints) from them
3. When you upload a photo, it finds the **closest match**
4. Lower distance = Higher confidence

**Key Point:** The system recognizes books by comparing uploaded photos against your reference library!

---

## 📸 Step 1: Collect Reference Book Cover Images

### Option A: Take Photos of Your Books

**Best Practices:**
- ✅ Good lighting (natural light or bright room)
- ✅ Cover fills most of the frame
- ✅ Straight-on angle (not tilted)
- ✅ Clear, in-focus image
- ✅ Cover is flat (not bent)

**Example workflow:**
```bash
# Take photos with your phone camera
# For each book in your library:
# 1. Place book on flat surface
# 2. Good lighting
# 3. Take straight-on photo
# 4. Make sure title is readable
```

**Tips:**
- 📱 Phone camera is fine!
- 💡 Natural window light is best
- 📐 Keep camera parallel to book
- 🔍 Zoom in so cover fills frame
- ✨ Avoid glare/reflections

### Option B: Download Cover Images

If you have ISBN numbers:
```python
# Example: Download from Open Library API
import requests

isbn = "9780743273565"  # The Great Gatsby
url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
response = requests.get(url)

with open(f"covers/{isbn}.jpg", "wb") as f:
    f.write(response.content)
```

### Option C: Scan Covers

If you have a scanner:
- Scan at 300 DPI
- Save as JPG
- Good color reproduction
- Cover should be clear

---

## 📁 Step 2: Organize Your Images

### Transfer to GMKtec M3

**From Phone (via USB):**
```bash
# Connect phone to GMKtec M3
# Copy photos to covers directory
cp /media/phone/DCIM/*.jpg /data/bookcv/covers/
```

**From Phone (via Network):**
```bash
# Use apps like "FTP Server" or "Solid Explorer"
# Or use Snapdrop (local network file sharing)
# Transfer to /data/bookcv/covers/
```

**From Computer (via SCP):**
```bash
# From your computer
scp book_covers/*.jpg scmc@scmc-M3:/data/bookcv/covers/
```

**From Computer (via Samba/Network Share):**
```bash
# Set up Samba share, then copy via file explorer
```

### Naming Convention

**Option 1: ISBN-based (Recommended)**
```
covers/
├── 9780743273565.jpg  (The Great Gatsby)
├── 9780262033848.jpg  (Introduction to Algorithms)
└── 9780060652920.jpg  (Mere Christianity)
```

**Option 2: Custom IDs**
```
covers/
├── book_001.jpg
├── book_002.jpg
└── book_003.jpg
```

**Option 3: Descriptive Names**
```
covers/
├── great_gatsby.jpg
├── intro_algorithms.jpg
└── mere_christianity.jpg
```

---

## 📝 Step 3: Create/Update meta.json

### Basic Template

```json
{
  "BOOK_ID_001": {
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "9780743273565",
    "image": "covers/great_gatsby.jpg"
  },
  "BOOK_ID_002": {
    "title": "Introduction to Algorithms",
    "author": "Thomas H. Cormen",
    "isbn": "9780262033848",
    "image": "covers/intro_algorithms.jpg"
  }
}
```

### Using ISBN as Book ID (Recommended)

```json
{
  "9780743273565": {
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "publisher": "Scribner",
    "year": "2004",
    "image": "covers/9780743273565.jpg"
  }
}
```

**Advantages:**
- Unique identifier
- Can integrate with library databases
- Easy to look up book info

### Quick Script to Generate meta.json

Create `create_metadata.py`:
```python
#!/usr/bin/env python3
import json
from pathlib import Path

# List all images in covers/
covers_dir = Path("covers")
images = list(covers_dir.glob("*.jpg")) + list(covers_dir.glob("*.png"))

meta = {}
for img in images:
    book_id = img.stem  # filename without extension
    meta[book_id] = {
        "title": f"Book {book_id}",  # Edit these manually
        "author": "Unknown",
        "image": str(img)
    }

with open("meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print(f"Created meta.json with {len(meta)} books")
print("Now edit meta.json to add proper titles and authors!")
```

Run it:
```bash
python3 create_metadata.py
nano meta.json  # Edit with actual book info
```

---

## 🧠 Step 4: Generate Embeddings

```bash
cd /data/bookcv
source venv/bin/activate
python3 generate_embeddings.py
```

**Expected output:**
```
Generated embeddings for 50 books → /data/bookcv/embeddings.npy
```

**What this does:**
- Loads each cover image
- Extracts visual features using MobileNet
- Creates a "fingerprint" for each book
- Saves all fingerprints to embeddings.npy

---

## 🚀 Step 5: Start Service and Test

```bash
uvicorn app:app --host 0.0.0.0 --port 8001
```

**Test it:**
1. Open web interface (cloudflare URL)
2. Take a NEW photo of one of your books
3. Upload it
4. Should match with high confidence!

---

## 📊 Understanding Confidence Scores

### Distance Values
- **0.0 - 0.3**: Excellent match (90-100% confidence) ✅
- **0.3 - 0.6**: Good match (70-90% confidence) ✅
- **0.6 - 1.0**: Moderate match (50-70% confidence) ⚠️
- **1.0+**: Poor match (<50% confidence) ❌

### How Confidence is Calculated
```python
confidence = max(0, (1 - distance / 2) * 100)
```

### Example Results
```json
{
  "candidates": ["9780743273565", "9780262033848"],
  "distance": [0.15, 0.89]
}
```

- First match: distance 0.15 → ~92% confidence ✅
- Second match: distance 0.89 → ~55% confidence ⚠️

---

## 💡 Tips for Best Results

### 1. Use High-Quality Reference Images

**Good Reference:**
- Clear, well-lit photo
- Cover fills the frame
- No blur or distortion
- Straight-on angle

**Bad Reference:**
- Blurry, dark
- Cover is small in frame
- Tilted or skewed
- Heavy glare

### 2. Take Photos Consistently

**When adding books AND when recognizing:**
- Same lighting conditions
- Same angle (straight-on)
- Same distance
- Cover clearly visible

### 3. Multiple Versions

If a book has different editions with different covers:
```json
{
  "gatsby_1925": {
    "title": "The Great Gatsby (1925 Edition)",
    "image": "covers/gatsby_1925.jpg"
  },
  "gatsby_2004": {
    "title": "The Great Gatsby (2004 Edition)",
    "image": "covers/gatsby_2004.jpg"
  }
}
```

### 4. Handle Similar Covers

Books from the same series might look similar:
- Include distinguishing features in reference photo
- Use good lighting to capture subtle differences
- Consider adding book spine/back cover to help distinguish

---

## 🔄 Complete Workflow Example

### Scenario: Adding 20 Books from Your Home Library

```bash
# Day 1: Collect Images
# 1. Take photos of all 20 books with phone
# 2. Good lighting, straight-on shots
# 3. Transfer to computer

# Day 2: Setup on GMKtec M3
cd /data/bookcv

# Create covers directory
mkdir -p covers

# Copy images from phone/computer
scp user@computer:~/book_photos/*.jpg covers/

# Check what you have
ls -la covers/
# Should see 20 .jpg files

# Day 3: Create Metadata
# Option A: Manual
nano meta.json
# Add all 20 books with titles, authors, image paths

# Option B: Quick template
python3 create_metadata.py
nano meta.json
# Edit the template with actual book info

# Day 4: Generate Embeddings
source venv/bin/activate
python3 generate_embeddings.py
# Output: Generated embeddings for 20 books

# Verify
ls -lh embeddings.npy
# Should be > 10KB (not 0 bytes!)

# Day 5: Start Service
uvicorn app:app --host 0.0.0.0 --port 8001

# Day 6: Test Recognition
# Open web interface
# Take NEW photos of your books (different angle/lighting)
# Upload and see matches with high confidence!
```

---

## 📈 Improving Recognition Accuracy

### 1. Add More Reference Images

For better accuracy, add multiple photos per book:
```python
# Modify generate_embeddings.py to average multiple photos
# Or just use the best quality photo
```

### 2. Image Preprocessing

Already handled by the system:
- Resizes to 224x224
- Normalizes colors
- Extracts features

### 3. Retake Poor Quality References

If recognition is poor:
```bash
# 1. Delete the low-quality image
rm covers/book_001.jpg

# 2. Retake photo with better lighting
# Copy new photo to covers/

# 3. Regenerate embeddings
python3 generate_embeddings.py

# 4. Restart service
```

---

## 🎯 Real-World Example

### Adding Your Personal Library (100 Books)

**Week 1: Photo Session**
```
Day 1-2: Take photos of all 100 books
- Set up good lighting area
- Photo station with consistent setup
- 2-3 minutes per book
- Total: 4-6 hours
```

**Week 2: Data Preparation**
```bash
# Transfer all photos to GMKtec M3
scp -r book_photos/* scmc@scmc-M3:/data/bookcv/covers/

# Create metadata file
cd /data/bookcv
python3 create_metadata.py

# Edit with book info (can use ISBN lookup APIs)
nano meta.json

# Or create a CSV and convert:
# title,author,isbn,image
# Import and convert to JSON
```

**Week 3: Generate and Test**
```bash
# Generate embeddings
python3 generate_embeddings.py
# Output: Generated embeddings for 100 books

# Start service
uvicorn app:app --host 0.0.0.0 --port 8001

# Test with 10 random books
# Should get high confidence matches!
```

---

## 🔧 Advanced: Batch Import Script

Create `batch_import.py`:
```python
#!/usr/bin/env python3
"""
Batch import books with ISBN lookup
"""
import json
import requests
from pathlib import Path

def lookup_isbn(isbn):
    """Lookup book info from Open Library"""
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    response = requests.get(url)
    data = response.json()
    
    key = f"ISBN:{isbn}"
    if key in data:
        book = data[key]
        return {
            "title": book.get("title", "Unknown"),
            "author": book.get("authors", [{}])[0].get("name", "Unknown"),
            "publisher": book.get("publishers", [{}])[0].get("name", "Unknown"),
        }
    return None

def main():
    covers_dir = Path("covers")
    images = list(covers_dir.glob("*.jpg"))
    
    meta = {}
    for img in images:
        isbn = img.stem
        
        # Try ISBN lookup
        if isbn.isdigit() and len(isbn) in [10, 13]:
            print(f"Looking up ISBN {isbn}...")
            info = lookup_isbn(isbn)
            if info:
                meta[isbn] = {
                    **info,
                    "isbn": isbn,
                    "image": str(img)
                }
                print(f"  ✓ Found: {info['title']}")
            else:
                print(f"  ✗ Not found")
                meta[isbn] = {
                    "title": f"Book {isbn}",
                    "author": "Unknown",
                    "isbn": isbn,
                    "image": str(img)
                }
        else:
            # Non-ISBN filename
            meta[isbn] = {
                "title": f"Book {isbn}",
                "author": "Unknown",
                "image": str(img)
            }
    
    with open("meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    
    print(f"\nCreated meta.json with {len(meta)} books")

if __name__ == "__main__":
    main()
```

Usage:
```bash
# Name your cover images with ISBNs
# covers/9780743273565.jpg
# covers/9780262033848.jpg

python3 batch_import.py
# Automatically looks up book info!
```

---

## ✅ Quality Checklist

Before generating embeddings:

- [ ] All cover images are in `covers/` directory
- [ ] Images are clear and well-lit
- [ ] Images are readable (can see title)
- [ ] `meta.json` has entry for each image
- [ ] Image paths in meta.json are correct
- [ ] No duplicate book IDs in meta.json
- [ ] Tested with `python3 verify_setup.py`

After generating embeddings:

- [ ] `embeddings.npy` file is > 1KB (not empty)
- [ ] No errors during generation
- [ ] Service starts without errors
- [ ] Test upload gives expected results

---

## 🎓 Summary

**To get high confidence results:**

1. **Add YOUR actual books** (not demo data)
2. **Take good quality photos** (clear, well-lit, straight-on)
3. **Create meta.json** with accurate book info
4. **Generate embeddings** from your photos
5. **Test with NEW photos** of the same books

**The system learns from YOUR reference images!**

The better your reference photos, the better the recognition will be. 📚✨

---

## 📞 Quick Help

```bash
# Check your setup
python3 verify_setup.py

# Verify embeddings
python3 -c "import numpy as np; a=np.load('embeddings.npy'); print(f'Books: {len(a)}, Size: {a.nbytes:,} bytes')"

# Test single book
python3 -c "
import cv2, json
from utils.embedding import get_embedding
img = cv2.imread('covers/your_book.jpg')
emb = get_embedding(img)
print(f'Embedding shape: {emb.shape}')
"
```

Ready to add your books? Start with a small batch (5-10 books) to test the workflow! 🚀

