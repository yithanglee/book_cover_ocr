"""
Enhanced Book Cover OCR Service with CLIP, SQLite, and Caching
Priority 1: Better accuracy with CLIP and cosine similarity
Priority 3: Scalability with database, async processing, and caching
"""
from fastapi import FastAPI, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import cv2
import numpy as np
from utils.embedding_v2 import (
    initialize_clip_model, 
    get_embedding, 
    assess_image_quality,
    compute_similarity
)
from utils.database import (
    BookDatabase, 
    initialize_database, 
    migrate_from_json,
    get_all_books_sync,
    get_book_ids_sync
)
import faiss
import json
import asyncio
from pathlib import Path
from cachetools import TTLCache, cached
from functools import wraps
import logging
import hashlib
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIDENCE_THRESHOLD = 0.65  # Minimum similarity score (0-1, higher = stricter)
TOP_K_RESULTS = 5
USE_HNSW = True  # Use HNSW for approximate nearest neighbor (faster for large datasets)
CACHE_SIZE = 1000
CACHE_TTL = 3600  # 1 hour

# Initialize FastAPI
app = FastAPI(
    title="Book Cover OCR Service - Enhanced",
    version="2.0.0",
    description="Enhanced book recognition with CLIP embeddings and smart matching"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount covers directory
covers_path = Path("covers")
if covers_path.exists():
    app.mount("/covers", StaticFiles(directory="covers"), name="covers")

# Global state
db = BookDatabase()
embeddings_array: Optional[np.ndarray] = None
faiss_index: Optional[faiss.Index] = None
book_ids_list: List[str] = []
embedding_cache = TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TTL)


def load_embeddings_and_index():
    """Load embeddings and build FAISS index with cosine similarity"""
    global embeddings_array, faiss_index, book_ids_list
    
    try:
        embeddings_array = np.load("embeddings.npy").astype("float32")
        book_ids_list = get_book_ids_sync()
        
        if len(book_ids_list) != len(embeddings_array):
            logger.warning(
                f"Mismatch: {len(book_ids_list)} books but {len(embeddings_array)} embeddings"
            )
        
        # Normalize embeddings for cosine similarity
        # With normalized vectors, cosine similarity = inner product
        faiss.normalize_L2(embeddings_array)
        
        dim = embeddings_array.shape[1]
        
        if USE_HNSW and len(embeddings_array) > 100:
            # HNSW for larger datasets (approximate but faster)
            M = 32  # Number of connections per layer
            faiss_index = faiss.IndexHNSWFlat(dim, M)
            faiss_index.hnsw.efConstruction = 40
            faiss_index.hnsw.efSearch = 16
            logger.info("Using HNSW index for approximate nearest neighbor")
        else:
            # Exact search with inner product (cosine similarity on normalized vectors)
            faiss_index = faiss.IndexFlatIP(dim)
            logger.info("Using flat index with cosine similarity")
        
        faiss_index.add(embeddings_array)
        logger.info(f"Loaded {len(embeddings_array)} embeddings, dimension={dim}")
        
    except FileNotFoundError:
        logger.warning("No embeddings.npy found. Database is empty.")
        embeddings_array = None
        faiss_index = None
    except Exception as e:
        logger.error(f"Failed to load embeddings: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize models and database on startup"""
    logger.info("Starting Book Cover OCR Service v2.0...")
    
    # Initialize database
    initialize_database()
    
    # Migrate from old JSON format if exists
    try:
        migrate_from_json()
    except Exception as e:
        logger.warning(f"Migration skipped: {e}")
    
    # Initialize CLIP model
    try:
        initialize_clip_model()
        logger.info("CLIP model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize CLIP: {e}")
        raise
    
    # Load embeddings and FAISS index
    load_embeddings_and_index()
    
    logger.info("Service started successfully!")


def hash_image(img: np.ndarray) -> str:
    """Generate hash for image caching"""
    return hashlib.md5(img.tobytes()).hexdigest()


def compute_confidence_score(similarity: float, rank: int = 1) -> Dict:
    """
    Convert similarity to confidence with interpretation
    
    Args:
        similarity: Cosine similarity (0-1)
        rank: Result rank (1 for top match)
    
    Returns:
        Dict with confidence score and match quality
    """
    # Adjust confidence based on similarity
    if similarity >= 0.85:
        quality = "excellent"
        confidence = "very_high"
    elif similarity >= 0.75:
        quality = "good"
        confidence = "high"
    elif similarity >= CONFIDENCE_THRESHOLD:
        quality = "acceptable"
        confidence = "medium"
    else:
        quality = "poor"
        confidence = "low"
    
    return {
        "similarity": float(similarity),
        "confidence": confidence,
        "match_quality": quality,
        "rank": rank
    }


async def recognize_image(img: np.ndarray) -> Dict:
    """
    Core recognition logic with confidence assessment
    
    Args:
        img: OpenCV image (BGR)
    
    Returns:
        Recognition results with confidence scores
    """
    if faiss_index is None or embeddings_array is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. No books indexed yet."
        )
    
    # Check image quality
    is_acceptable, quality_msg = assess_image_quality(img)
    if not is_acceptable:
        return {
            "status": "error",
            "error": quality_msg,
            "suggestion": "Please provide a clearer, well-lit image"
        }
    
    # Check cache
    img_hash = hash_image(img)
    if img_hash in embedding_cache:
        emb = embedding_cache[img_hash]
        logger.info("Using cached embedding")
    else:
        # Generate embedding
        emb = get_embedding(img, use_clip=True)
        embedding_cache[img_hash] = emb
    
    # Normalize for cosine similarity
    emb = emb.reshape(1, -1).astype("float32")
    faiss.normalize_L2(emb)
    
    # Search (returns similarity scores with IndexFlatIP)
    similarities, indices = faiss_index.search(emb, TOP_K_RESULTS)
    
    # Process results
    candidates = []
    top_similarity = similarities[0][0] if len(similarities[0]) > 0 else 0.0
    
    for rank, (idx, similarity) in enumerate(zip(indices[0], similarities[0]), 1):
        if idx >= len(book_ids_list):
            continue
        
        book_id = book_ids_list[idx]
        book_info = await db.get_book(book_id)
        
        if book_info:
            confidence_info = compute_confidence_score(similarity, rank)
            candidates.append({
                "book_id": book_id,
                "title": book_info["title"],
                "author": book_info["author"],
                "image": book_info["image"],
                **confidence_info
            })
    
    # Determine overall match status
    if top_similarity < CONFIDENCE_THRESHOLD:
        return {
            "status": "no_match",
            "message": "No confident match found",
            "threshold": CONFIDENCE_THRESHOLD,
            "top_similarity": float(top_similarity),
            "suggestion": "Book may not be in database or image quality is insufficient",
            "possible_matches": candidates[:3] if candidates else []
        }
    else:
        return {
            "status": "success",
            "message": "Match found",
            "results": candidates,
            "top_match": candidates[0] if candidates else None
        }


@app.get("/")
async def root():
    """Serve the web interface"""
    return FileResponse("static/index.html")


@app.get("/admin")
async def admin():
    """Serve the admin interface"""
    return FileResponse("static/admin.html")


@app.get("/health")
async def health():
    """Enhanced health check with model and database status"""
    book_count = await db.count_books()
    
    return {
        "status": "healthy",
        "version": "2.0.0",
        "model": "CLIP ViT-B/32",
        "search_algorithm": "HNSW" if USE_HNSW else "Flat",
        "similarity_metric": "cosine",
        "books_indexed": book_count,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "cache_size": len(embedding_cache),
        "database": "sqlite"
    }


@app.post("/recognize")
async def recognize(file: UploadFile):
    """Recognize a book from an uploaded image with confidence scoring"""
    try:
        # Read and decode image
        data = await file.read()
        
        # Check file size (limit to 20MB)
        if len(data) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 20MB)")
        
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Perform recognition
        result = await recognize_image(img)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recognition error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Recognition failed: {str(e)}")


@app.post("/recognize_base64")
async def recognize_base64(data: dict):
    """Recognize a book from a base64 encoded image"""
    try:
        import base64
        
        img_data = base64.b64decode(data["image"])
        
        if len(img_data) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 20MB)")
        
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        result = await recognize_image(img)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recognition error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/books")
async def list_books(limit: int = None, offset: int = 0):
    """List all indexed books with pagination"""
    books = await db.get_all_books(limit=limit, offset=offset)
    total = await db.count_books()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "books": books
    }


@app.get("/books/{book_id}")
async def get_book(book_id: str):
    """Get details of a specific book"""
    book = await db.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/search")
async def search_books(q: str, limit: int = 10):
    """Search books by title or author"""
    results = await db.search_books(q, limit=limit)
    return {"query": q, "count": len(results), "results": results}


async def regenerate_embeddings_async():
    """Regenerate all embeddings asynchronously (background task)"""
    global embeddings_array, faiss_index, book_ids_list
    
    logger.info("Starting background embedding regeneration...")
    
    try:
        books = await db.get_all_books()
        book_ids_list = [book['book_id'] for book in books]
        embeddings = []
        
        for book in books:
            img_path = Path(book['image'])
            if not img_path.exists():
                logger.warning(f"Image not found: {img_path}")
                continue
            
            img = cv2.imread(str(img_path))
            if img is None:
                logger.warning(f"Cannot read image: {img_path}")
                continue
            
            emb = get_embedding(img, use_clip=True)
            embeddings.append(emb)
        
        if embeddings:
            embeddings_array = np.vstack(embeddings).astype("float32")
            np.save("embeddings.npy", embeddings_array)
            
            # Rebuild FAISS index
            load_embeddings_and_index()
            
            logger.info(f"Successfully regenerated {len(embeddings)} embeddings")
        else:
            logger.warning("No embeddings generated")
            
    except Exception as e:
        logger.error(f"Embedding regeneration failed: {e}", exc_info=True)


@app.post("/admin/add_book")
async def add_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = None,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(None),
    publisher: str = Form(None)
):
    """Admin endpoint to add a new book to the library"""
    import uuid
    import shutil
    
    try:
        # Generate unique book ID
        book_id = isbn if isbn else f"BOOK_{uuid.uuid4().hex[:8].upper()}"
        
        # Check if book already exists
        existing = await db.get_book(book_id)
        if existing:
            raise HTTPException(status_code=400, detail=f"Book {book_id} already exists")
        
        # Save cover image
        covers_dir = Path("covers")
        covers_dir.mkdir(exist_ok=True)
        
        file_extension = Path(file.filename).suffix or ".jpg"
        image_filename = f"{book_id}{file_extension}"
        image_path = covers_dir / image_filename
        
        # Save uploaded file
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add to database
        success = await db.add_book(
            book_id=book_id,
            title=title,
            author=author,
            image_path=str(image_path),
            isbn=isbn,
            publisher=publisher
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add book to database")
        
        # Regenerate embeddings in background
        background_tasks.add_task(regenerate_embeddings_async)
        
        total_books = await db.count_books()
        
        return {
            "success": True,
            "book_id": book_id,
            "message": f"Book '{title}' added successfully",
            "total_books": total_books,
            "note": "Embeddings are being regenerated in the background"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add book: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/admin/delete_book/{book_id}")
async def delete_book(book_id: str, background_tasks: BackgroundTasks):
    """Admin endpoint to delete a book from the library"""
    book = await db.get_book(book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        # Delete image file
        image_path = Path(book["image"])
        if image_path.exists():
            image_path.unlink()
        
        # Delete from database
        success = await db.delete_book(book_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete book")
        
        # Regenerate embeddings in background
        background_tasks.add_task(regenerate_embeddings_async)
        
        total_books = await db.count_books()
        
        return {
            "success": True,
            "message": f"Book {book_id} deleted",
            "total_books": total_books,
            "note": "Embeddings are being regenerated in the background"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete book: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/rebuild_index")
async def rebuild_index(background_tasks: BackgroundTasks):
    """Manually trigger index rebuild"""
    background_tasks.add_task(regenerate_embeddings_async)
    return {
        "success": True,
        "message": "Index rebuild started in background"
    }


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    total_books = await db.count_books()
    
    return {
        "total_books": total_books,
        "embedding_dimension": embeddings_array.shape[1] if embeddings_array is not None else 0,
        "cache_size": len(embedding_cache),
        "cache_capacity": CACHE_SIZE,
        "model": "CLIP ViT-B/32",
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "search_algorithm": "HNSW" if USE_HNSW else "Flat Index"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

