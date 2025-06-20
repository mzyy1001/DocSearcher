#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检索脚本：输入问题 → 返回最相关的若干 chunk（文本 + 距离）
"""

import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

import json
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

VECTOR_DIR   = Path("vector_store/faiss_index")
MODEL_PATH   = "./models/m3e-base" 
TOP_K        = 5

print("🔄  Loading m3e-base (embedding model)…")
embed_model = SentenceTransformer(MODEL_PATH)

print("🔄  Loading FAISS index…")
index = faiss.read_index(str(VECTOR_DIR / "index.faiss"))

with open(VECTOR_DIR / "metadata.json", encoding="utf-8") as f:
    metadata = json.load(f)


def search(query: str, top_k: int = TOP_K):
    """给定自然语言问题 → 返回 (chunks, distances)"""
    vec = embed_model.encode([query], convert_to_numpy=True)[0].astype("float32")
    distances, idx = index.search(np.expand_dims(vec, axis=0), top_k)
    hits = []
    for rank, (i, dist) in enumerate(zip(idx[0], distances[0]), 1):
        meta = metadata[i]
        hits.append({
            "rank": rank,
            "distance": float(dist),
            "source_file": meta["source_file"],
            "chunk_index": meta["chunk_index"],
            "text": meta["text"]
        })
    return hits


if __name__ == "__main__":
    import argparse, textwrap
    parser = argparse.ArgumentParser(description="Chunk retriever")
    parser.add_argument("question", nargs="+", help="问题文本")
    args = parser.parse_args()

    question = " ".join(args.question)
    results = search(question)

    print("\n🧩 Top chunks:")
    for hit in results:
        print(textwrap.indent(
            f"\n[Rank {hit['rank']} | Dist {hit['distance']:.4f}] "
            f"{hit['source_file']}#{hit['chunk_index']}\n{hit['text']}",
            "  "
        ))
