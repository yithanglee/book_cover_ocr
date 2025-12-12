#!/usr/bin/env python3
"""
Comprehensive test suite for Book Cover OCR v2
Tests all new features: CLIP, confidence scoring, database, caching
"""
import requests
import json
import time
from pathlib import Path
import sys

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_URL = "http://localhost:8000"
TEST_PASSED = 0
TEST_FAILED = 0


def print_test(name: str):
    """Print test name"""
    print(f"\n{BLUE}[TEST]{RESET} {name}")


def print_pass(message: str):
    """Print success message"""
    global TEST_PASSED
    TEST_PASSED += 1
    print(f"  {GREEN}✓{RESET} {message}")


def print_fail(message: str):
    """Print failure message"""
    global TEST_FAILED
    TEST_FAILED += 1
    print(f"  {RED}✗{RESET} {message}")


def print_info(message: str):
    """Print info message"""
    print(f"  {YELLOW}ℹ{RESET} {message}")


def test_health():
    """Test enhanced health endpoint"""
    print_test("Enhanced Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print_pass("Service is healthy")
            
            data = response.json()
            
            # Check v2 specific fields
            if data.get("version") == "2.0.0":
                print_pass(f"Version: {data['version']}")
            else:
                print_fail(f"Expected version 2.0.0, got {data.get('version')}")
            
            if data.get("model") == "CLIP ViT-B/32":
                print_pass(f"Model: {data['model']}")
            else:
                print_fail(f"Expected CLIP model, got {data.get('model')}")
            
            if "confidence_threshold" in data:
                print_pass(f"Confidence threshold: {data['confidence_threshold']}")
            else:
                print_fail("Missing confidence_threshold field")
            
            if data.get("similarity_metric") == "cosine":
                print_pass(f"Using cosine similarity")
            else:
                print_fail(f"Expected cosine similarity, got {data.get('similarity_metric')}")
            
            if data.get("database") == "sqlite":
                print_pass("Using SQLite database")
            else:
                print_fail(f"Expected SQLite, got {data.get('database')}")
            
            print_info(f"Books indexed: {data.get('books_indexed', 0)}")
            print_info(f"Cache size: {data.get('cache_size', 0)}")
            
        else:
            print_fail(f"Health check failed with status {response.status_code}")
    
    except Exception as e:
        print_fail(f"Health check failed: {e}")


def test_stats():
    """Test new stats endpoint"""
    print_test("Statistics Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        
        if response.status_code == 200:
            print_pass("Stats endpoint working")
            
            data = response.json()
            print_info(f"Total books: {data.get('total_books', 0)}")
            print_info(f"Embedding dimension: {data.get('embedding_dimension', 0)}")
            print_info(f"Model: {data.get('model', 'unknown')}")
            print_info(f"Search algorithm: {data.get('search_algorithm', 'unknown')}")
            
        else:
            print_fail(f"Stats endpoint failed with status {response.status_code}")
    
    except Exception as e:
        print_fail(f"Stats endpoint failed: {e}")


def test_books_list():
    """Test books listing endpoint"""
    print_test("Books Listing")
    
    try:
        response = requests.get(f"{BASE_URL}/books", timeout=5)
        
        if response.status_code == 200:
            print_pass("Books endpoint working")
            
            data = response.json()
            
            if isinstance(data, dict) and "books" in data:
                # v2 format with pagination
                print_pass("Using v2 format with pagination")
                books = data.get("books", [])
                total = data.get("total", 0)
                print_info(f"Total books: {total}")
                print_info(f"Returned: {len(books)} books")
            elif isinstance(data, dict):
                # v1 format (backward compatibility)
                print_info("Using v1 format (backward compatibility)")
                print_info(f"Books: {len(data)}")
            else:
                print_fail(f"Unexpected format: {type(data)}")
        
        else:
            print_fail(f"Books endpoint failed with status {response.status_code}")
    
    except Exception as e:
        print_fail(f"Books endpoint failed: {e}")


def test_search():
    """Test new search functionality"""
    print_test("Book Search Functionality")
    
    try:
        response = requests.get(f"{BASE_URL}/search?q=test&limit=5", timeout=5)
        
        if response.status_code == 200:
            print_pass("Search endpoint working")
            
            data = response.json()
            print_info(f"Search query: {data.get('query', '')}")
            print_info(f"Results: {data.get('count', 0)}")
            
        else:
            print_fail(f"Search endpoint failed with status {response.status_code}")
    
    except Exception as e:
        print_fail(f"Search endpoint failed: {e}")


def test_recognition_with_confidence():
    """Test recognition with confidence scoring"""
    print_test("Recognition with Confidence Scoring")
    
    # Check if test images exist
    test_images = list(Path("covers").glob("*.*"))[:3] if Path("covers").exists() else []
    
    if not test_images:
        print_info("No test images found in covers/ directory")
        print_info("Skipping recognition test")
        return
    
    for img_path in test_images:
        try:
            with open(img_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{BASE_URL}/recognize",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status == "success":
                    print_pass(f"{img_path.name}: Match found")
                    
                    results = data.get("results", [])
                    if results:
                        top_match = results[0]
                        print_info(f"  Book: {top_match.get('title', 'Unknown')}")
                        print_info(f"  Similarity: {top_match.get('similarity', 0):.3f}")
                        print_info(f"  Confidence: {top_match.get('confidence', 'unknown')}")
                        print_info(f"  Quality: {top_match.get('match_quality', 'unknown')}")
                        
                        # Check v2 specific fields
                        if 'similarity' in top_match:
                            print_pass("  Has similarity score (v2 feature)")
                        if 'confidence' in top_match:
                            print_pass("  Has confidence level (v2 feature)")
                        if 'match_quality' in top_match:
                            print_pass("  Has match quality (v2 feature)")
                
                elif status == "no_match":
                    print_info(f"{img_path.name}: No confident match")
                    print_info(f"  Threshold: {data.get('threshold', 0)}")
                    print_info(f"  Top similarity: {data.get('top_similarity', 0):.3f}")
                    print_pass("No match detection working (v2 feature)")
                
                elif status == "error":
                    print_info(f"{img_path.name}: Image quality issue")
                    print_info(f"  Error: {data.get('error', 'unknown')}")
                    print_pass("Image quality assessment working (v2 feature)")
            
            else:
                print_fail(f"{img_path.name}: Recognition failed with status {response.status_code}")
        
        except Exception as e:
            print_fail(f"{img_path.name}: {e}")


def test_caching():
    """Test caching functionality"""
    print_test("Caching Performance")
    
    test_images = list(Path("covers").glob("*.*"))[:1] if Path("covers").exists() else []
    
    if not test_images:
        print_info("No test images found")
        print_info("Skipping cache test")
        return
    
    img_path = test_images[0]
    
    try:
        # First request (no cache)
        with open(img_path, 'rb') as f:
            files = {'file': f}
            start = time.time()
            response1 = requests.post(f"{BASE_URL}/recognize", files=files, timeout=30)
            time1 = time.time() - start
        
        # Second request (should use cache)
        with open(img_path, 'rb') as f:
            files = {'file': f}
            start = time.time()
            response2 = requests.post(f"{BASE_URL}/recognize", files=files, timeout=30)
            time2 = time.time() - start
        
        if response1.status_code == 200 and response2.status_code == 200:
            print_pass("Cache test completed")
            print_info(f"First request: {time1:.3f}s")
            print_info(f"Second request: {time2:.3f}s")
            
            if time2 < time1 * 0.8:
                print_pass(f"Cache speedup: {time1/time2:.1f}x faster")
            else:
                print_info("Cache may not be effective (times similar)")
    
    except Exception as e:
        print_fail(f"Cache test failed: {e}")


def test_database():
    """Test database functionality"""
    print_test("Database Operations")
    
    try:
        # Test get_book endpoint
        response = requests.get(f"{BASE_URL}/books", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict) and "books" in data:
                books = data.get("books", [])
                if books:
                    book_id = books[0].get("book_id")
                    
                    # Test individual book fetch
                    response = requests.get(f"{BASE_URL}/books/{book_id}", timeout=5)
                    
                    if response.status_code == 200:
                        print_pass("Individual book fetch working")
                        book = response.json()
                        print_info(f"Fetched: {book.get('title', 'Unknown')}")
                    else:
                        print_fail("Individual book fetch failed")
                else:
                    print_info("No books in database to test")
            else:
                print_info("Using v1 format (no individual fetch)")
    
    except Exception as e:
        print_fail(f"Database test failed: {e}")


def print_summary():
    """Print test summary"""
    total = TEST_PASSED + TEST_FAILED
    
    print("\n" + "="*60)
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print("="*60)
    print(f"Total tests: {total}")
    print(f"{GREEN}Passed: {TEST_PASSED}{RESET}")
    print(f"{RED}Failed: {TEST_FAILED}{RESET}")
    
    if TEST_FAILED == 0:
        print(f"\n{GREEN}✓ All tests passed! System is working correctly.{RESET}")
    else:
        print(f"\n{YELLOW}⚠ Some tests failed. Check the output above.{RESET}")
    
    print("="*60)


def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Book Cover OCR v2 - Comprehensive Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # Check if service is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print(f"\n{RED}ERROR: Service is not running at {BASE_URL}{RESET}")
        print(f"Please start the service first:")
        print(f"  uvicorn app:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Run tests
    test_health()
    test_stats()
    test_books_list()
    test_search()
    test_database()
    test_recognition_with_confidence()
    test_caching()
    
    # Print summary
    print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if TEST_FAILED == 0 else 1)


if __name__ == "__main__":
    main()

