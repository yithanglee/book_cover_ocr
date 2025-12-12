#!/usr/bin/env python3
"""
Watch a folder for new images and automatically process them
Usage: python watch_folder.py /path/to/watch/folder
"""

import sys
import time
import requests
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from datetime import datetime


API_URL = "http://localhost:8000/recognize"


class ImageHandler(FileSystemEventHandler):
    """Handle new image files"""
    
    def __init__(self, output_dir=None):
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        self.output_dir = Path(output_dir) if output_dir else None
        if self.output_dir:
            self.output_dir.mkdir(exist_ok=True)
        self.processing = set()
    
    def on_created(self, event):
        """Process newly created files"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's an image file
        if file_path.suffix.lower() not in self.image_extensions:
            return
        
        # Avoid processing the same file multiple times
        if file_path in self.processing:
            return
        
        self.processing.add(file_path)
        
        # Wait a bit for file to be fully written
        time.sleep(0.5)
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] New image detected: {file_path.name}")
        self.process_image(file_path)
        
        self.processing.remove(file_path)
    
    def process_image(self, image_path: Path):
        """Process a single image"""
        try:
            with open(image_path, 'rb') as f:
                response = requests.post(API_URL, files={"file": f}, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.handle_success(image_path, result)
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error processing {image_path.name}: {e}")
    
    def handle_success(self, image_path: Path, result: dict):
        """Handle successful recognition"""
        candidates = result["candidates"]
        distances = result["distance"]
        
        print(f"✓ Successfully processed")
        print(f"  Top matches:")
        for i, (book_id, distance) in enumerate(zip(candidates[:3], distances[:3]), 1):
            confidence = max(0, (1 - distance / 2) * 100)
            print(f"    {i}. {book_id} (distance: {distance:.4f}, confidence: {confidence:.1f}%)")
        
        # Save result to file if output directory specified
        if self.output_dir:
            result_file = self.output_dir / f"{image_path.stem}_result.json"
            result_data = {
                "timestamp": datetime.now().isoformat(),
                "image": str(image_path),
                "result": result
            }
            with open(result_file, 'w') as f:
                json.dump(result_data, f, indent=2)
            print(f"  Result saved to: {result_file}")


def watch_folder(folder: str, output_dir: str = None):
    """Watch a folder for new images"""
    watch_path = Path(folder)
    
    if not watch_path.exists():
        print(f"Error: Directory {folder} does not exist")
        return
    
    print(f"👁️  Watching folder: {watch_path}")
    if output_dir:
        print(f"📁 Results will be saved to: {output_dir}")
    print(f"🔄 Waiting for new images... (Press Ctrl+C to stop)\n")
    
    event_handler = ImageHandler(output_dir)
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Stopping folder watcher...")
        observer.stop()
    
    observer.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python watch_folder.py <watch_directory> [output_directory]")
        sys.exit(1)
    
    folder = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    watch_folder(folder, output_dir)

