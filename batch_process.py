#!/usr/bin/env python3
"""
Batch process multiple book cover images from a directory
Usage: python batch_process.py /path/to/images/
"""

import requests
import sys
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://localhost:8000/recognize"
MAX_WORKERS = 4  # Adjust based on your system


def process_image(image_path: Path):
    """Process a single image"""
    try:
        with open(image_path, 'rb') as f:
            response = requests.post(API_URL, files={"file": f}, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            return {
                "file": image_path.name,
                "status": "success",
                "result": result
            }
        else:
            return {
                "file": image_path.name,
                "status": "error",
                "error": response.text
            }
    except Exception as e:
        return {
            "file": image_path.name,
            "status": "error",
            "error": str(e)
        }


def batch_process(directory: str, output_file: str = None):
    """Process all images in a directory"""
    image_dir = Path(directory)
    
    if not image_dir.exists():
        print(f"Error: Directory {directory} does not exist")
        return
    
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [
        f for f in image_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        print(f"No image files found in {directory}")
        return
    
    print(f"Found {len(image_files)} images to process")
    print(f"Processing with {MAX_WORKERS} workers...\n")
    
    results = []
    
    # Process images in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {
            executor.submit(process_image, img): img
            for img in image_files
        }
        
        for i, future in enumerate(as_completed(future_to_file), 1):
            result = future.result()
            results.append(result)
            
            # Print progress
            status_symbol = "✓" if result["status"] == "success" else "✗"
            print(f"[{i}/{len(image_files)}] {status_symbol} {result['file']}")
            
            if result["status"] == "success":
                candidates = result["result"]["candidates"]
                distances = result["result"]["distance"]
                print(f"    Top match: {candidates[0]} (distance: {distances[0]:.4f})")
            else:
                print(f"    Error: {result['error']}")
            print()
    
    # Save results to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")
    
    # Summary
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n{'='*50}")
    print(f"Summary: {success_count}/{len(results)} images processed successfully")
    print(f"{'='*50}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py <directory> [output_file.json]")
        sys.exit(1)
    
    directory = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    batch_process(directory, output_file)

