import os
import json
from docx import Document as DocxDocument
from pathlib import Path

# 配置
DATA_DIR = "data"
CHUNK_DIR = "chunks"
CHUNK_SIZE = 500  
OVERLAP = 50

os.makedirs(CHUNK_DIR, exist_ok=True)


def docx_to_text(filepath):
    doc = DocxDocument(filepath)
    lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    return "\n".join(lines)


def load_text(filepath):
    if filepath.endswith(".docx"):
        return docx_to_text(filepath)
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()


def chunk_by_line(text, max_chars=CHUNK_SIZE, overlap=OVERLAP):
    lines = text.splitlines()
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if current_length + len(line) + 1 <= max_chars:
            current_chunk.append(line)
            current_length += len(line) + 1
        else:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
            overlap_lines = []
            running_len = 0
            for l in reversed(current_chunk):
                if running_len + len(l) + 1 <= overlap:
                    overlap_lines.insert(0, l)
                    running_len += len(l) + 1
                else:
                    break
            current_chunk = overlap_lines + [line]
            current_length = sum(len(l) + 1 for l in current_chunk)

    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return chunks


def process_all_documents():
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt") or filename.endswith(".docx"):
            filepath = os.path.join(DATA_DIR, filename)
            print(f"Processing: {filename}")
            text = load_text(filepath)
            chunks = chunk_by_line(text)
            chunk_path = os.path.join(CHUNK_DIR, f"{Path(filename).stem}_chunks.json")
            with open(chunk_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(chunks)} chunks → {chunk_path}")


if __name__ == "__main__":
    process_all_documents()
