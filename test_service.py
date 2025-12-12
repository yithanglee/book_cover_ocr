#!/usr/bin/env python3
"""
Test script for Book Cover OCR Service
Verifies that the service is running and responding correctly
"""

import requests
import sys
import time
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")


def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")


def test_service_running(base_url):
    """Test if service is running"""
    print_info("Testing if service is running...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Service is running!")
            print(f"  Status: {data.get('status')}")
            print(f"  Books indexed: {data.get('books_indexed')}")
            return True
        else:
            print_error(f"Service returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to service. Is it running?")
        print_info(f"Start with: uvicorn app:app --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_required_files():
    """Test if required files exist"""
    print_info("Checking required files...")
    
    required_files = {
        "embeddings.npy": "Embeddings file",
        "meta.json": "Metadata file",
        "models/mobilenet.onnx": "Model file"
    }
    
    all_present = True
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print_success(f"{description}: {file_path}")
        else:
            print_error(f"Missing {description}: {file_path}")
            all_present = False
    
    return all_present


def test_books_list(base_url):
    """Test listing books"""
    print_info("Testing book listing...")
    try:
        response = requests.get(f"{base_url}/books", timeout=5)
        if response.status_code == 200:
            books = response.json()
            print_success(f"Successfully retrieved {len(books)} books")
            
            # Show first 3 books
            for i, (book_id, info) in enumerate(list(books.items())[:3], 1):
                title = info.get('title', 'N/A')
                author = info.get('author', 'N/A')
                print(f"  {i}. {book_id}: {title} by {author}")
            
            if len(books) > 3:
                print(f"  ... and {len(books) - 3} more books")
            
            return True
        else:
            print_error(f"Failed to retrieve books: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_image_recognition(base_url):
    """Test image recognition (if test image available)"""
    print_info("Testing image recognition...")
    
    # Try to find any image file for testing
    test_images = list(Path(".").glob("*.jpg")) + list(Path(".").glob("*.png"))
    
    if not test_images:
        print_warning("No test images found. Skipping recognition test.")
        print_info("To test recognition, place a .jpg or .png image in this directory")
        return None
    
    test_image = test_images[0]
    print_info(f"Using test image: {test_image}")
    
    try:
        with open(test_image, 'rb') as f:
            response = requests.post(
                f"{base_url}/recognize",
                files={"file": f},
                timeout=10
            )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Image recognition successful!")
            
            candidates = result.get('candidates', [])
            distances = result.get('distance', [])
            
            print(f"  Top match: {candidates[0] if candidates else 'None'}")
            if distances:
                print(f"  Distance: {distances[0]:.4f}")
            
            print("\n  All candidates:")
            for i, (book_id, distance) in enumerate(zip(candidates, distances), 1):
                confidence = max(0, (1 - distance / 2) * 100)
                print(f"    {i}. {book_id} - distance: {distance:.4f} (confidence: {confidence:.1f}%)")
            
            return True
        else:
            print_error(f"Recognition failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_web_interface(base_url):
    """Test if web interface is accessible"""
    print_info("Testing web interface...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print_success("Web interface is accessible")
            print_info(f"Open in browser: {base_url}")
            return True
        else:
            print_error(f"Web interface returned: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print_header("Book Cover OCR Service - Test Suite")
    
    # Configuration
    base_url = "http://localhost:8000"
    
    print_info(f"Testing service at: {base_url}\n")
    
    # Run tests
    results = {}
    
    print_header("Test 1: Required Files")
    results['files'] = test_required_files()
    
    print_header("Test 2: Service Status")
    results['service'] = test_service_running(base_url)
    
    if not results['service']:
        print_error("\nService is not running. Cannot continue tests.")
        print_info("Please start the service first:")
        print_info("  uvicorn app:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print_header("Test 3: Books List")
    results['books'] = test_books_list(base_url)
    
    print_header("Test 4: Web Interface")
    results['web'] = test_web_interface(base_url)
    
    print_header("Test 5: Image Recognition")
    results['recognition'] = test_image_recognition(base_url)
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    failed = sum(1 for v in results.values() if v is False)
    total = len(results)
    
    print(f"Total tests: {total}")
    print_success(f"Passed: {passed}")
    if skipped > 0:
        print_warning(f"Skipped: {skipped}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    print("\n" + "="*60)
    
    if failed == 0:
        print_success("All tests passed! Service is ready to use. 🎉")
        print_info(f"\nAccess the service at: {base_url}")
        print_info("Read QUICK_START.md for usage instructions")
    else:
        print_error("Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

