#!/usr/bin/env python3
"""
Verify the setup of Book Cover OCR service
Checks all required files and dependencies
"""

import os
import sys
from pathlib import Path
import json

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        size = Path(filepath).stat().st_size
        if size > 0:
            print_success(f"{description}: {filepath} ({size:,} bytes)")
            return True
        else:
            print_error(f"{description} is empty (0 bytes): {filepath}")
            return False
    else:
        print_error(f"{description} not found: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if Path(dirpath).exists() and Path(dirpath).is_dir():
        count = len(list(Path(dirpath).iterdir()))
        print_success(f"{description}: {dirpath} ({count} items)")
        return True
    else:
        print_error(f"{description} not found: {dirpath}")
        return False

def check_covers_and_meta():
    """Check if covers directory matches meta.json"""
    if not Path("meta.json").exists():
        return False
    
    try:
        with open("meta.json", 'r') as f:
            meta = json.load(f)
        
        print_info(f"Found {len(meta)} books in meta.json")
        
        missing_images = []
        for book_id, info in meta.items():
            image_path = info.get("image", "")
            if not Path(image_path).exists():
                missing_images.append(image_path)
        
        if missing_images:
            print_error(f"Missing {len(missing_images)} cover images:")
            for img in missing_images[:5]:  # Show first 5
                print(f"  - {img}")
            if len(missing_images) > 5:
                print(f"  ... and {len(missing_images) - 5} more")
            return False
        else:
            print_success(f"All {len(meta)} cover images exist")
            return True
    except json.JSONDecodeError:
        print_error("meta.json is not valid JSON")
        return False
    except Exception as e:
        print_error(f"Error checking meta.json: {e}")
        return False

def check_dependencies():
    """Check if Python dependencies are installed"""
    required = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'onnxruntime': 'ONNX Runtime',
        'faiss': 'FAISS'
    }
    
    all_installed = True
    for module, name in required.items():
        try:
            __import__(module)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed (import {module})")
            all_installed = False
    
    return all_installed

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Book Cover OCR - Setup Verification{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    os.chdir(Path(__file__).parent)
    print_info(f"Working directory: {os.getcwd()}\n")
    
    all_ok = True
    
    # Check required files
    print(f"{Colors.BOLD}1. Checking Required Files:{Colors.END}")
    all_ok &= check_file_exists("app.py", "Main application")
    all_ok &= check_file_exists("utils/embedding.py", "Embedding utilities")
    all_ok &= check_file_exists("models/mobilenet.onnx", "MobileNet model")
    all_ok &= check_file_exists("requirements.txt", "Requirements file")
    print()
    
    # Check data files
    print(f"{Colors.BOLD}2. Checking Data Files:{Colors.END}")
    meta_ok = check_file_exists("meta.json", "Book metadata")
    emb_ok = check_file_exists("embeddings.npy", "Embeddings database")
    all_ok &= meta_ok and emb_ok
    print()
    
    # Check covers directory
    print(f"{Colors.BOLD}3. Checking Covers Directory:{Colors.END}")
    covers_ok = check_directory_exists("covers", "Book covers directory")
    all_ok &= covers_ok
    print()
    
    # Check covers match meta
    if meta_ok and covers_ok:
        print(f"{Colors.BOLD}4. Verifying Cover Images:{Colors.END}")
        all_ok &= check_covers_and_meta()
        print()
    
    # Check dependencies
    print(f"{Colors.BOLD}5. Checking Python Dependencies:{Colors.END}")
    deps_ok = check_dependencies()
    all_ok &= deps_ok
    print()
    
    # Summary
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    if all_ok:
        print_success("All checks passed! ✨")
        print(f"\n{Colors.GREEN}Your setup is ready!{Colors.END}")
        print(f"\n{Colors.BOLD}Start the service:{Colors.END}")
        print(f"  uvicorn app:app --host 0.0.0.0 --port 8001")
    else:
        print_error("Some checks failed!")
        print(f"\n{Colors.YELLOW}What to do:{Colors.END}")
        
        if not emb_ok or not meta_ok or not covers_ok:
            print(f"\n{Colors.BOLD}Option 1: Create Demo Data (for testing){Colors.END}")
            print(f"  python3 create_demo_data.py")
            
            print(f"\n{Colors.BOLD}Option 2: Add Your Own Books{Colors.END}")
            print(f"  1. Create covers/ directory")
            print(f"  2. Add your book cover images")
            print(f"  3. Edit meta.json with your books")
            print(f"  4. Run: python3 generate_embeddings.py")
            
            print(f"\n{Colors.BLUE}See SETUP_INSTRUCTIONS.md for detailed steps{Colors.END}")
        
        if not deps_ok:
            print(f"\n{Colors.BOLD}Install dependencies:{Colors.END}")
            print(f"  pip install -r requirements.txt")
    
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

