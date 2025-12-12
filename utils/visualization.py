"""
Visualization utilities for book cover recognition
Shows preprocessing steps, quality checks, and feature extraction
"""
import cv2
import numpy as np
from typing import Tuple, Dict, List
import base64


def draw_quality_indicators(img: np.ndarray, quality_info: Dict) -> np.ndarray:
    """
    Draw quality check indicators on the image
    
    Args:
        img: Original image
        quality_info: Dict with quality metrics
    
    Returns:
        Image with quality indicators drawn
    """
    vis_img = img.copy()
    h, w = vis_img.shape[:2]
    
    # Draw border based on quality
    is_acceptable = quality_info.get('acceptable', True)
    border_color = (0, 255, 0) if is_acceptable else (0, 0, 255)
    cv2.rectangle(vis_img, (5, 5), (w-5, h-5), border_color, 3)
    
    # Add quality text
    y_offset = 30
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Resolution
    resolution_text = f"Resolution: {w}x{h}"
    cv2.putText(vis_img, resolution_text, (10, y_offset), font, 0.6, (255, 255, 255), 2)
    cv2.putText(vis_img, resolution_text, (10, y_offset), font, 0.6, (0, 255, 0), 1)
    y_offset += 30
    
    # Brightness
    if 'brightness' in quality_info:
        brightness = quality_info['brightness']
        brightness_text = f"Brightness: {brightness:.1f}"
        cv2.putText(vis_img, brightness_text, (10, y_offset), font, 0.6, (255, 255, 255), 2)
        cv2.putText(vis_img, brightness_text, (10, y_offset), font, 0.6, (0, 255, 0), 1)
        y_offset += 30
    
    # Sharpness
    if 'sharpness' in quality_info:
        sharpness = quality_info['sharpness']
        sharpness_text = f"Sharpness: {sharpness:.1f}"
        cv2.putText(vis_img, sharpness_text, (10, y_offset), font, 0.6, (255, 255, 255), 2)
        cv2.putText(vis_img, sharpness_text, (10, y_offset), font, 0.6, (0, 255, 0), 1)
        y_offset += 30
    
    # Overall status
    status = "✓ Good Quality" if is_acceptable else "✗ Poor Quality"
    status_color = (0, 255, 0) if is_acceptable else (0, 0, 255)
    cv2.putText(vis_img, status, (10, y_offset), font, 0.7, (255, 255, 255), 2)
    cv2.putText(vis_img, status, (10, y_offset), font, 0.7, status_color, 1)
    
    return vis_img


def draw_processing_grid(img: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    Show how the image is resized and processed for the model
    
    Args:
        img: Original image
        target_size: Target size for model input
    
    Returns:
        Image showing resize operation
    """
    h, w = img.shape[:2]
    vis_img = img.copy()
    
    # Draw grid showing how image will be resized
    grid_color = (255, 255, 0)  # Cyan
    
    # Calculate resize region (center crop simulation)
    aspect_ratio = w / h
    target_aspect = target_size[0] / target_size[1]
    
    if aspect_ratio > target_aspect:
        # Image is wider - will crop sides
        new_w = int(h * target_aspect)
        x_offset = (w - new_w) // 2
        cv2.rectangle(vis_img, (x_offset, 0), (x_offset + new_w, h), grid_color, 3)
        
        # Draw crop indicators
        cv2.line(vis_img, (0, 0), (x_offset, 0), (0, 0, 255), 2)
        cv2.line(vis_img, (w, 0), (x_offset + new_w, 0), (0, 0, 255), 2)
    else:
        # Image is taller - will crop top/bottom
        new_h = int(w / target_aspect)
        y_offset = (h - new_h) // 2
        cv2.rectangle(vis_img, (0, y_offset), (w, y_offset + new_h), grid_color, 3)
        
        # Draw crop indicators
        cv2.line(vis_img, (0, 0), (0, y_offset), (0, 0, 255), 2)
        cv2.line(vis_img, (0, h), (0, y_offset + new_h), (0, 0, 255), 2)
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"Resize: {w}x{h} → {target_size[0]}x{target_size[1]}"
    cv2.putText(vis_img, text, (10, h - 20), font, 0.6, (255, 255, 255), 2)
    cv2.putText(vis_img, text, (10, h - 20), font, 0.6, grid_color, 1)
    
    return vis_img


def draw_corner_detection(img: np.ndarray) -> np.ndarray:
    """
    Detect and draw corners (simulating feature extraction)
    
    Args:
        img: Original image
    
    Returns:
        Image with corners drawn
    """
    vis_img = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect corners
    corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
    
    if corners is not None:
        corners = np.int0(corners)
        for corner in corners:
            x, y = corner.ravel()
            # Draw small circles at corner points
            cv2.circle(vis_img, (x, y), 3, (0, 255, 255), -1)
            cv2.circle(vis_img, (x, y), 5, (255, 0, 255), 1)
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"Features: {len(corners) if corners is not None else 0} points"
    cv2.putText(vis_img, text, (10, 30), font, 0.7, (255, 255, 255), 2)
    cv2.putText(vis_img, text, (10, 30), font, 0.7, (0, 255, 255), 1)
    
    return vis_img


def draw_attention_regions(img: np.ndarray, grid_size: int = 7) -> np.ndarray:
    """
    Draw grid showing attention regions (simulating CLIP patch processing)
    
    Args:
        img: Original image
        grid_size: Number of patches (CLIP uses 7x7 patches for 224x224)
    
    Returns:
        Image with attention grid
    """
    vis_img = img.copy()
    h, w = vis_img.shape[:2]
    
    # Calculate patch size
    patch_h = h // grid_size
    patch_w = w // grid_size
    
    # Draw grid
    for i in range(1, grid_size):
        # Vertical lines
        cv2.line(vis_img, (i * patch_w, 0), (i * patch_w, h), (0, 255, 0), 1)
        # Horizontal lines
        cv2.line(vis_img, (0, i * patch_h), (w, i * patch_h), (0, 255, 0), 1)
    
    # Draw border
    cv2.rectangle(vis_img, (0, 0), (w-1, h-1), (0, 255, 0), 2)
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"CLIP Patches: {grid_size}x{grid_size}"
    cv2.putText(vis_img, text, (10, 30), font, 0.7, (255, 255, 255), 2)
    cv2.putText(vis_img, text, (10, 30), font, 0.7, (0, 255, 0), 1)
    
    # Simulate attention by highlighting some patches
    # (In real CLIP, this would be based on actual attention scores)
    np.random.seed(42)  # Consistent visualization
    for i in range(grid_size):
        for j in range(grid_size):
            if np.random.random() > 0.7:  # Highlight ~30% of patches
                x1 = j * patch_w
                y1 = i * patch_h
                x2 = x1 + patch_w
                y2 = y1 + patch_h
                overlay = vis_img.copy()
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)
                cv2.addWeighted(overlay, 0.2, vis_img, 0.8, 0, vis_img)
    
    return vis_img


def create_processing_pipeline(img: np.ndarray, quality_info: Dict = None) -> List[Dict]:
    """
    Create a complete visualization pipeline showing all processing steps
    
    Args:
        img: Original image
        quality_info: Quality assessment results
    
    Returns:
        List of dicts with step name and base64 encoded image
    """
    steps = []
    
    # Step 1: Original image
    _, buffer = cv2.imencode('.jpg', img)
    steps.append({
        'name': '1. Original Image',
        'description': 'Uploaded book cover image',
        'image': base64.b64encode(buffer).decode('utf-8')
    })
    
    # Step 2: Quality indicators
    if quality_info:
        quality_img = draw_quality_indicators(img, quality_info)
        _, buffer = cv2.imencode('.jpg', quality_img)
        steps.append({
            'name': '2. Quality Assessment',
            'description': 'Checking resolution, brightness, and sharpness',
            'image': base64.b64encode(buffer).decode('utf-8')
        })
    
    # Step 3: Resize visualization
    resize_img = draw_processing_grid(img)
    _, buffer = cv2.imencode('.jpg', resize_img)
    steps.append({
        'name': '3. Resize Operation',
        'description': 'Image resized to 224x224 for model input',
        'image': base64.b64encode(buffer).decode('utf-8')
    })
    
    # Step 4: Feature extraction
    features_img = draw_corner_detection(img)
    _, buffer = cv2.imencode('.jpg', features_img)
    steps.append({
        'name': '4. Feature Detection',
        'description': 'Key visual features detected in the image',
        'image': base64.b64encode(buffer).decode('utf-8')
    })
    
    # Step 5: CLIP patches
    attention_img = draw_attention_regions(img)
    _, buffer = cv2.imencode('.jpg', attention_img)
    steps.append({
        'name': '5. CLIP Patch Processing',
        'description': 'Image divided into patches for CLIP model',
        'image': base64.b64encode(buffer).decode('utf-8')
    })
    
    return steps


def get_quality_metrics(img: np.ndarray) -> Dict:
    """
    Get detailed quality metrics for visualization
    
    Args:
        img: Input image
    
    Returns:
        Dict with quality metrics
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Brightness
    brightness = np.mean(gray)
    
    # Sharpness (Laplacian variance)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Determine if acceptable
    acceptable = (
        h >= 100 and w >= 100 and
        brightness >= 20 and
        sharpness >= 50
    )
    
    return {
        'resolution': (w, h),
        'brightness': float(brightness),
        'sharpness': float(sharpness),
        'acceptable': acceptable
    }


def encode_image_to_base64(img: np.ndarray) -> str:
    """
    Encode OpenCV image to base64 string
    
    Args:
        img: OpenCV image
    
    Returns:
        Base64 encoded string
    """
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

