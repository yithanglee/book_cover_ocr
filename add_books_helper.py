#!/usr/bin/env python3
"""
Interactive helper script to add books to your library
Makes it easy to create meta.json entries
"""

import json
from pathlib import Path
import sys

def list_cover_images():
    """List all images in covers directory"""
    covers_dir = Path("covers")
    if not covers_dir.exists():
        covers_dir.mkdir()
        print("Created covers/ directory")
        return []
    
    images = list(covers_dir.glob("*.jpg")) + list(covers_dir.glob("*.png")) + list(covers_dir.glob("*.jpeg"))
    return sorted(images)

def load_or_create_meta():
    """Load existing meta.json or create new"""
    meta_file = Path("meta.json")
    if meta_file.exists():
        try:
            with open(meta_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_meta(meta):
    """Save meta.json"""
    with open("meta.json", 'w') as f:
        json.dump(meta, f, indent=2)

def add_book_interactive(image_path):
    """Interactively add book information"""
    print(f"\n{'='*60}")
    print(f"Adding book: {image_path.name}")
    print(f"{'='*60}")
    
    # Suggest book ID from filename
    default_id = image_path.stem
    book_id = input(f"Book ID [{default_id}]: ").strip() or default_id
    
    title = input("Title: ").strip()
    if not title:
        print("❌ Title is required!")
        return None
    
    author = input("Author: ").strip() or "Unknown"
    
    # Optional fields
    isbn = input("ISBN (optional): ").strip()
    publisher = input("Publisher (optional): ").strip()
    year = input("Year (optional): ").strip()
    
    book_data = {
        "title": title,
        "author": author,
        "image": str(image_path)
    }
    
    if isbn:
        book_data["isbn"] = isbn
    if publisher:
        book_data["publisher"] = publisher
    if year:
        book_data["year"] = year
    
    return book_id, book_data

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║          Book Cover OCR - Add Books Helper                 ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # List images
    images = list_cover_images()
    
    if not images:
        print("❌ No images found in covers/ directory!")
        print("\nPlease add your book cover images to covers/ first:")
        print("  mkdir -p covers")
        print("  cp your_book_covers/*.jpg covers/")
        return 1
    
    print(f"✓ Found {len(images)} images in covers/\n")
    
    # Load existing meta
    meta = load_or_create_meta()
    existing_images = {Path(info["image"]) for info in meta.values()}
    
    # Find new images
    new_images = [img for img in images if img not in existing_images]
    
    if not new_images:
        print("✓ All images already in meta.json!")
        print(f"  Total books: {len(meta)}")
        print("\nTo modify existing entries, edit meta.json directly:")
        print("  nano meta.json")
        return 0
    
    print(f"Found {len(new_images)} new images to add:\n")
    for i, img in enumerate(new_images, 1):
        print(f"  {i}. {img.name}")
    
    print(f"\n{len(meta)} books already in database")
    print(f"{len(new_images)} new books to add\n")
    
    # Ask how to proceed
    print("Options:")
    print("  [1] Add all books interactively (recommended)")
    print("  [2] Create template (edit meta.json manually)")
    print("  [3] Cancel")
    
    choice = input("\nChoice [1]: ").strip() or "1"
    
    if choice == "1":
        # Interactive mode
        added = 0
        for img in new_images:
            result = add_book_interactive(img)
            if result:
                book_id, book_data = result
                meta[book_id] = book_data
                added += 1
                print(f"✓ Added {book_id}")
            
            # Ask to continue
            if img != new_images[-1]:
                cont = input("\nContinue to next book? [Y/n]: ").strip().lower()
                if cont == 'n':
                    break
        
        save_meta(meta)
        print(f"\n✓ Saved {added} new books to meta.json")
        print(f"  Total books: {len(meta)}")
        
    elif choice == "2":
        # Template mode
        for img in new_images:
            book_id = img.stem
            meta[book_id] = {
                "title": f"EDIT: {book_id}",
                "author": "EDIT: Author name",
                "image": str(img)
            }
        
        save_meta(meta)
        print(f"\n✓ Created template in meta.json")
        print(f"  Added {len(new_images)} placeholders")
        print(f"\nNow edit meta.json:")
        print(f"  nano meta.json")
        print(f"\nReplace 'EDIT:' entries with actual book information")
        
    else:
        print("\n❌ Cancelled")
        return 0
    
    # Next steps
    print(f"\n{'='*60}")
    print("Next steps:")
    print("{'='*60}")
    print("1. Review meta.json:")
    print("   cat meta.json")
    print("\n2. Generate embeddings:")
    print("   python3 generate_embeddings.py")
    print("\n3. Start service:")
    print("   uvicorn app:app --host 0.0.0.0 --port 8001")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)

