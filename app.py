from fastapi import FastAPI, UploadFile
import cv2, numpy as np
from utils.embedding import get_embedding
import faiss, json
import numpy as np
emb_array = np.load("embeddings.npy").astype("float32")

index = faiss.IndexFlatL2(emb_array.shape[1])
index.add(emb_array)

app = FastAPI()

meta = json.load(open("meta.json"))


@app.post("/recognize")
async def recognize(file: UploadFile):
    data = await file.read()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

    emb = get_embedding(img).astype("float32")
    D, I = index.search(emb, 5)


    book_ids = list(meta.keys())
    result_ids = [book_ids[idx] for idx in I[0]]

    return {"candidates": result_ids, "distance": D[0].tolist()}
