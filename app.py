from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import cv2, numpy as np
from utils.embedding import get_embedding
import faiss, json
import numpy as np
from pathlib import Path

emb_array = np.load("embeddings.npy").astype("float32")

index = faiss.IndexFlatL2(emb_array.shape[1])
index.add(emb_array)

app = FastAPI(title="Book Cover OCR Service", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount covers directory for serving cover images
from pathlib import Path as PathLib
covers_path = PathLib("covers")
if covers_path.exists():
    app.mount("/covers", StaticFiles(directory="covers"), name="covers")

meta = json.load(open("meta.json"))


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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": True,
        "books_indexed": len(meta)
    }


@app.post("/recognize")
async def recognize(file: UploadFile):
    """Recognize a book from an uploaded image"""
    try:
        data = await file.read()
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        emb = get_embedding(img).astype("float32")
        D, I = index.search(emb, 5)

        book_ids = list(meta.keys())
        result_ids = [book_ids[idx] for idx in I[0]]

        return {"candidates": result_ids, "distance": D[0].tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recognize_base64")
async def recognize_base64(data: dict):
    """Recognize a book from a base64 encoded image"""
    try:
        import base64
        
        img_data = base64.b64decode(data["image"])
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        emb = get_embedding(img).astype("float32")
        D, I = index.search(emb, 5)

        book_ids = list(meta.keys())
        result_ids = [book_ids[idx] for idx in I[0]]

        return {"candidates": result_ids, "distance": D[0].tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/books")
async def list_books():
    """List all indexed books"""
    return meta


@app.post("/admin/add_book")
async def add_book(
    file: UploadFile,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(None),
    publisher: str = Form(None)
):
    """Admin endpoint to add a new book to the library"""
    import uuid
    import shutil
    from pathlib import Path
    
    try:
        # Generate unique book ID
        book_id = isbn if isbn else f"BOOK_{uuid.uuid4().hex[:8].upper()}"
        
        # Save cover image
        covers_dir = Path("covers")
        covers_dir.mkdir(exist_ok=True)
        
        file_extension = Path(file.filename).suffix or ".jpg"
        image_filename = f"{book_id}{file_extension}"
        image_path = covers_dir / image_filename
        
        # Save uploaded file
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update meta.json
        book_data = {
            "title": title,
            "author": author,
            "image": str(image_path)
        }
        if isbn:
            book_data["isbn"] = isbn
        if publisher:
            book_data["publisher"] = publisher
        
        meta[book_id] = book_data
        
        # Save meta.json
        with open("meta.json", "w") as f:
            json.dump(meta, f, indent=2)
        
        # Regenerate embeddings
        import cv2
        img = cv2.imread(str(image_path))
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        emb = get_embedding(img).astype("float32")
        
        # Append to embeddings
        emb_array_current = np.load("embeddings.npy").astype("float32")
        emb_array_new = np.vstack([emb_array_current, emb])
        np.save("embeddings.npy", emb_array_new)
        
        # Reload FAISS index
        global index
        index = faiss.IndexFlatL2(emb_array_new.shape[1])
        index.add(emb_array_new)
        
        return {
            "success": True,
            "book_id": book_id,
            "message": f"Book '{title}' added successfully",
            "total_books": len(meta)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/admin/delete_book/{book_id}")
async def delete_book(book_id: str):
    """Admin endpoint to delete a book from the library"""
    from pathlib import Path
    
    if book_id not in meta:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        # Delete image file
        image_path = Path(meta[book_id]["image"])
        if image_path.exists():
            image_path.unlink()
        
        # Remove from meta
        del meta[book_id]
        
        # Save meta.json
        with open("meta.json", "w") as f:
            json.dump(meta, f, indent=2)
        
        # Regenerate all embeddings
        embeddings = []
        for bid, info in meta.items():
            img_path = Path(info["image"])
            img = cv2.imread(str(img_path))
            if img is not None:
                emb = get_embedding(img)
                embeddings.append(emb)
        
        if embeddings:
            emb_array = np.vstack(embeddings).astype("float32")
            np.save("embeddings.npy", emb_array)
            
            # Reload FAISS index
            global index
            index = faiss.IndexFlatL2(emb_array.shape[1])
            index.add(emb_array)
        
        return {
            "success": True,
            "message": f"Book {book_id} deleted",
            "total_books": len(meta)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
