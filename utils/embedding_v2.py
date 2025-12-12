"""
Enhanced embedding module with CLIP support and better preprocessing
"""
import cv2
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Global model instances (loaded once)
_clip_model: Optional[CLIPModel] = None
_clip_processor: Optional[CLIPProcessor] = None
_device: Optional[str] = None


def initialize_clip_model(model_name: str = "openai/clip-vit-base-patch32"):
    """
    Initialize CLIP model globally (called once at startup)
    Using ViT-B/32 for balance between accuracy and speed on CPU
    """
    global _clip_model, _clip_processor, _device
    
    if _clip_model is not None:
        logger.info("CLIP model already initialized")
        return
    
    try:
        logger.info(f"Loading CLIP model: {model_name}")
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {_device}")
        
        _clip_model = CLIPModel.from_pretrained(model_name).to(_device)
        _clip_processor = CLIPProcessor.from_pretrained(model_name)
        
        # Set to eval mode and disable gradients for inference
        _clip_model.eval()
        torch.set_grad_enabled(False)
        
        logger.info("CLIP model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load CLIP model: {e}")
        raise


def preprocess_image(img: np.ndarray) -> Image.Image:
    """
    Enhanced image preprocessing for better recognition
    
    Args:
        img: OpenCV image (BGR format)
    
    Returns:
        PIL Image ready for CLIP processing
    """
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Basic quality enhancements
    # 1. Increase contrast slightly
    img_rgb = cv2.convertScaleAbs(img_rgb, alpha=1.1, beta=10)
    
    # 2. Denoise if needed (optional, can be slow)
    # img_rgb = cv2.fastNlMeansDenoisingColored(img_rgb, None, 10, 10, 7, 21)
    
    # Convert to PIL Image
    pil_img = Image.fromarray(img_rgb)
    
    return pil_img


def get_clip_embedding(img: np.ndarray) -> np.ndarray:
    """
    Get CLIP visual embedding from an image
    
    Args:
        img: OpenCV image (BGR format)
    
    Returns:
        Normalized embedding vector (512-dim for ViT-B/32)
    """
    if _clip_model is None or _clip_processor is None:
        raise RuntimeError("CLIP model not initialized. Call initialize_clip_model() first.")
    
    # Preprocess image
    pil_img = preprocess_image(img)
    
    # Process through CLIP
    inputs = _clip_processor(images=pil_img, return_tensors="pt")
    inputs = {k: v.to(_device) for k, v in inputs.items()}
    
    with torch.no_grad():
        image_features = _clip_model.get_image_features(**inputs)
    
    # Normalize embedding (for cosine similarity)
    embedding = image_features.cpu().numpy()[0]
    embedding = embedding / np.linalg.norm(embedding)
    
    return embedding.astype(np.float32)


def get_embedding(img: np.ndarray, use_clip: bool = True) -> np.ndarray:
    """
    Main embedding function with model selection
    
    Args:
        img: OpenCV image (BGR format)
        use_clip: If True, use CLIP; if False, fallback to MobileNet
    
    Returns:
        Normalized embedding vector
    """
    if use_clip:
        return get_clip_embedding(img)
    else:
        # Fallback to old MobileNet implementation
        from .embedding import get_embedding as get_mobilenet_embedding
        return get_mobilenet_embedding(img)


def compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Cosine similarity score (0 to 1, higher is better)
    """
    # Cosine similarity = dot product of normalized vectors
    similarity = np.dot(embedding1, embedding2)
    return float(similarity)


def assess_image_quality(img: np.ndarray) -> Tuple[bool, str]:
    """
    Assess if an image is suitable for recognition
    
    Args:
        img: OpenCV image (BGR format)
    
    Returns:
        Tuple of (is_acceptable, reason)
    """
    h, w = img.shape[:2]
    
    # Check minimum resolution
    if h < 100 or w < 100:
        return False, f"Image resolution too low: {w}x{h} (minimum 100x100)"
    
    # Check if image is too dark
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    if mean_brightness < 20:
        return False, f"Image too dark (brightness: {mean_brightness:.1f})"
    
    # Check if image is too blurry (Laplacian variance)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 50:
        return False, f"Image too blurry (sharpness: {laplacian_var:.1f})"
    
    return True, "Image quality acceptable"


# Backward compatibility
__all__ = [
    'initialize_clip_model',
    'get_embedding',
    'get_clip_embedding',
    'compute_similarity',
    'assess_image_quality',
    'preprocess_image'
]

