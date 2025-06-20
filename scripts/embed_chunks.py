import os
import json
from pathlib import Path
import shutil

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


DATA_DIR = Path("data")
if DATA_DIR.exists():
    print("🧹 清空 data/ 目录 …")
    shutil.rmtree(DATA_DIR)
DATA_DIR.mkdir(exist_ok=True)

os.environ["CUDA_VISIBLE_DEVICES"] = ""  # ban GPU
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
CHUNK_DIR = "chunks"
VECTOR_STORE_DIR = "vector_store/faiss_index"
EMBEDDING_DIM = 768  # m3e-base

os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

print("🚀 Loading m3e-base model...")
model = SentenceTransformer("./models/m3e-base")

index = faiss.IndexFlatL2(EMBEDDING_DIM)
metadata = []

for filename in os.listdir(CHUNK_DIR):
    if filename.endswith("_chunks.json"):
        chunk_path = os.path.join(CHUNK_DIR, filename)
        with open(chunk_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        print(f"🧩 Embedding {filename} ({len(chunks)} chunks)")
        embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
        index.add(embeddings)
        metadata.extend([{
            "source_file": filename,
            "chunk_index": i,
            "text": chunks[i]
        } for i in range(len(chunks))])

faiss.write_index(index, os.path.join(VECTOR_STORE_DIR, "index.faiss"))

with open(os.path.join(VECTOR_STORE_DIR, "metadata.json"), "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"✅ Finished! {len(metadata)} chunks embedded and saved.")
