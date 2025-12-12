#!/usr/bin/env python3
"""
Example client for the Book Cover OCR service
Demonstrates different ways to send images to the service
"""

import requests
import base64
from pathlib import Path


class BookOCRClient:
    """Client for Book Cover OCR Service"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if service is running"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}
    
    def recognize_from_file(self, image_path):
        """Recognize book from image file"""
        with open(image_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/recognize",
                files={"file": f}
            )
        return response.json()
    
    def recognize_from_base64(self, image_path):
        """Recognize book from base64 encoded image"""
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
        
        response = requests.post(
            f"{self.base_url}/recognize_base64",
            json={"image": img_data}
        )
        return response.json()
    
    def list_books(self):
        """Get list of all indexed books"""
        response = requests.get(f"{self.base_url}/books")
        return response.json()


def main():
    """Example usage"""
    # Initialize client
    client = BookOCRClient("http://localhost:8000")
    
    # Check health
    print("Checking service health...")
    health = client.health_check()
    print(f"Status: {health}")
    print()
    
    if health.get("status") != "healthy":
        print("⚠️  Service is not available!")
        return
    
    # Example: Recognize from file
    image_path = "test_cover.jpg"  # Replace with your image path
    
    if Path(image_path).exists():
        print(f"Recognizing book from: {image_path}")
        result = client.recognize_from_file(image_path)
        
        print("\n📚 Recognition Results:")
        print(f"  Top match: {result['candidates'][0]}")
        print(f"  Distance: {result['distance'][0]:.4f}")
        print(f"\n  All candidates:")
        for i, (book_id, distance) in enumerate(zip(result['candidates'], result['distance']), 1):
            confidence = max(0, (1 - distance / 2) * 100)
            print(f"    {i}. {book_id} - distance: {distance:.4f} (confidence: {confidence:.1f}%)")
    else:
        print(f"⚠️  Image file not found: {image_path}")
    
    # List all books
    print("\n\n📚 All indexed books:")
    books = client.list_books()
    for book_id, info in list(books.items())[:5]:  # Show first 5
        print(f"  {book_id}: {info.get('title', 'N/A')} by {info.get('author', 'N/A')}")
    print(f"  ... and {len(books) - 5} more books")


if __name__ == "__main__":
    main()

