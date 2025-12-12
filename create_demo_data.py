#!/usr/bin/env python3
"""
Create demo data for testing the Book Cover OCR service
This generates sample book covers and embeddings for testing
"""

import os
import json
import numpy as np
import cv2
from pathlib import Path

BASE_PATH = Path(__file__).parent
COVERS_PATH = BASE_PATH / "covers"
META_PATH = BASE_PATH / "meta.json"
EMBEDDINGS_PATH = BASE_PATH / "embeddings.npy"

# Demo books
DEMO_BOOKS = {
    "DEMO001": {
        "title": "Demo Book 1 - Red",
        "author": "Demo Author",
        "image": "covers/demo_001.jpg"
    },
    "DEMO002": {
        "title": "Demo Book 2 - Blue",
        "author": "Demo Author",
        "image": "covers/demo_002.jpg"
    },
    "DEMO003": {
        "title": "Demo Book 3 - Green",
        "author": "Demo Author",
        "image": "covers/demo_003.jpg"
    }
}

def create_demo_cover(color, filename):
    """Create a simple colored demo book cover"""
    # Create a 224x224 image with text
    img = np.zeros((400, 300, 3), dtype=np.uint8)
    
    # Fill with color
    if color == "red":
        img[:, :] = [50, 50, 200]  # BGR format
    elif color == "blue":
        img[:, :] = [200, 50, 50]
    elif color == "green":
        img[:, :] = [50, 200, 50]
    
    # Add some pattern to make it unique
    cv2.rectangle(img, (50, 50), (250, 350), (255, 255, 255), 3)
    cv2.putText(img, "DEMO", (80, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    cv2.putText(img, color.upper(), (70, 280), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    
    # Save
    cv2.imwrite(str(filename), img)
    print(f"✓ Created demo cover: {filename}")

def main():
    print("="*60)
    print("Creating Demo Data for Book Cover OCR")
    print("="*60)
    print()
    
    # Create covers directory
    COVERS_PATH.mkdir(exist_ok=True)
    print(f"✓ Created directory: {COVERS_PATH}")
    
    # Create demo cover images
    print("\nCreating demo book covers...")
    create_demo_cover("red", COVERS_PATH / "demo_001.jpg")
    create_demo_cover("blue", COVERS_PATH / "demo_002.jpg")
    create_demo_cover("green", COVERS_PATH / "demo_003.jpg")
    
    # Create meta.json
    print("\nCreating meta.json...")
    with open(META_PATH, 'w') as f:
        json.dump(DEMO_BOOKS, f, indent=2)
    print(f"✓ Created: {META_PATH}")
    
    # Generate embeddings
    print("\nGenerating embeddings...")
    from utils.embedding import get_embedding
    
    embeddings = []
    for book_id, info in DEMO_BOOKS.items():
        cover_path = BASE_PATH / info["image"]
        img = cv2.imread(str(cover_path))
        if img is None:
            raise ValueError(f"Cannot read: {cover_path}")
        
        emb = get_embedding(img)
        embeddings.append(emb)
        print(f"✓ Generated embedding for {book_id}")
    
    # Save embeddings
    emb_array = np.vstack(embeddings).astype("float32")
    np.save(EMBEDDINGS_PATH, emb_array)
    print(f"✓ Saved embeddings to: {EMBEDDINGS_PATH}")
    
    # Verify
    print("\n" + "="*60)
    print("Demo Data Created Successfully!")
    print("="*60)
    print(f"\n📁 Files created:")
    print(f"  - {len(DEMO_BOOKS)} demo covers in covers/")
    print(f"  - meta.json with {len(DEMO_BOOKS)} books")
    print(f"  - embeddings.npy ({emb_array.shape})")
    print(f"\n🚀 You can now start the service:")
    print(f"  uvicorn app:app --host 0.0.0.0 --port 8001")
    print(f"\n⚠️  Note: This is DEMO data for testing only!")
    print(f"   Replace with real book covers when ready.")
    print(f"   See SETUP_INSTRUCTIONS.md for details.")

if __name__ == "__main__":
    main()

