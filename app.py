from fastapi import FastAPI, UploadFile, HTTPException
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

meta = json.load(open("meta.json"))


@app.get("/")
async def root():
    """Serve the web interface"""
    return FileResponse("static/index.html")


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
