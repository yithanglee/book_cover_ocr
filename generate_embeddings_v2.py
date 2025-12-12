#!/usr/bin/env python3
"""
Generate CLIP embeddings for all books in the database
Uses the new CLIP model and SQLite database
"""
import os
import numpy as np
from utils.embedding_v2 import initialize_clip_model, get_embedding
from utils.database import get_all_books_sync, get_book_ids_sync, DB_PATH
import cv2
from pathlib import Path
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_PATH = Path(__file__).parent
OUTPUT_EMBEDDINGS = BASE_PATH / "embeddings.npy"


def generate_embeddings(use_clip: bool = True):
    """
    Generate embeddings for all books in the database
    
    Args:
        use_clip: If True, use CLIP model; if False, use old MobileNet
    """
    logger.info("Starting embedding generation...")
    
    # Initialize CLIP model if needed
    if use_clip:
        logger.info("Initializing CLIP model...")
        initialize_clip_model()
    
    # Load books from database
    books = get_all_books_sync(DB_PATH)
    book_ids = get_book_ids_sync(DB_PATH)
    
    if not books:
        logger.error("No books found in database!")
        return
    
    logger.info(f"Found {len(books)} books in database")
    
    embeddings = []
    failed_books = []
    
    # Generate embeddings with progress bar
    for book_id in tqdm(book_ids, desc="Generating embeddings"):
        book_info = books.get(book_id)
        if not book_info:
            logger.warning(f"Book {book_id} not found in metadata")
            continue
        
        cover_file = BASE_PATH / book_info["image"]
        
        if not cover_file.exists():
            logger.warning(f"Image not found: {cover_file}")
            failed_books.append((book_id, "Image file not found"))
            continue
        
        try:
            img = cv2.imread(str(cover_file))
            if img is None:
                raise ValueError(f"Cannot read image: {cover_file}")
            
            # Generate embedding
            emb = get_embedding(img, use_clip=use_clip)
            embeddings.append(emb)
            
            logger.debug(f"✓ Generated embedding for {book_id}: {book_info['title']}")
            
        except Exception as e:
            logger.error(f"Failed to process {book_id}: {e}")
            failed_books.append((book_id, str(e)))
    
    # Save embeddings
    if embeddings:
        emb_array = np.vstack(embeddings).astype("float32")
        np.save(OUTPUT_EMBEDDINGS, emb_array)
        logger.info(f"✓ Successfully generated {len(embeddings)} embeddings → {OUTPUT_EMBEDDINGS}")
        logger.info(f"  Embedding dimension: {emb_array.shape[1]}")
        logger.info(f"  Model: {'CLIP ViT-B/32' if use_clip else 'MobileNet'}")
    else:
        logger.error("No embeddings were generated!")
        return
    
    # Report failures
    if failed_books:
        logger.warning(f"\n{len(failed_books)} books failed:")
        for book_id, error in failed_books:
            logger.warning(f"  - {book_id}: {error}")
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info(f"Summary:")
    logger.info(f"  Total books: {len(book_ids)}")
    logger.info(f"  Successful: {len(embeddings)}")
    logger.info(f"  Failed: {len(failed_books)}")
    logger.info("="*50)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate book cover embeddings")
    parser.add_argument(
        "--model",
        choices=["clip", "mobilenet"],
        default="clip",
        help="Model to use for embeddings (default: clip)"
    )
    
    args = parser.parse_args()
    
    use_clip = args.model == "clip"
    
    logger.info(f"Using model: {args.model.upper()}")
    generate_embeddings(use_clip=use_clip)

