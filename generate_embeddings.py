import os, json, numpy as np
from utils.embedding import get_embedding
import cv2

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
META_PATH = os.path.join(BASE_PATH, "meta.json")
COVERS_PATH = os.path.join(BASE_PATH, "covers")
OUTPUT_EMBEDDINGS = os.path.join(BASE_PATH, "embeddings.npy")

# Load metadata
meta = json.load(open(META_PATH))
book_ids = list(meta.keys())

embeddings = []

for book_id in book_ids:
    cover_file = os.path.join(BASE_PATH, meta[book_id]["image"])
    img = cv2.imread(cover_file)
    if img is None:
        raise ValueError(f"Cannot read image: {cover_file}")
    emb = get_embedding(img)
    embeddings.append(emb)

# Stack and save
emb_array = np.vstack(embeddings).astype("float32")
np.save(OUTPUT_EMBEDDINGS, emb_array)

print(f"Generated embeddings for {len(book_ids)} books → {OUTPUT_EMBEDDINGS}")
