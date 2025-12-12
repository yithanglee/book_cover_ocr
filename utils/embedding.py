import cv2, numpy as np, onnxruntime as ort

session = ort.InferenceSession("models/mobilenet.onnx")

def get_embedding(img):
    img = cv2.resize(img, (224, 224))
    img = img.astype(np.float32) / 255.0
    x = np.transpose(img, (2,0,1))[None, ...]
    emb = session.run(None, {"x": x})[0]
    return emb / np.linalg.norm(emb)
