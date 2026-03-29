from rag import get_collection
from PyPDF2 import PdfReader
import json
import os

DATA_DIR = "data"

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def chunk_text(text, chunk_size=300, overlap=50):
    """Rough chunk text by word-count so that embedding is hyper-focused."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def ingest_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    collection = get_collection()
    
    file_count = 0
    
        # Process files
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        
        # 1. Handle Structured JSON (Our new brain format)
        if filename.endswith(".json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    
                    # If it's our new structured RAG format
                    if isinstance(items, list) and len(items) > 0 and 'content' in items[0]:
                        print(f"📦 Starting batch upload for {filename} ({len(items)} items)...")
                        
                        # Process in small batches (e.g., 20 at a time) for more reliable upload
                        batch_size = 20
                        for i in range(0, len(items), batch_size):
                            batch = items[i:i + batch_size]
                            batch_docs = [it['content'] for it in batch]
                            batch_metas = [it['metadata'] for it in batch]
                            batch_ids = [f"{filename}_{idx}" for idx in range(i, i + len(batch))]
                            
                            collection.upsert(
                                documents=batch_docs, 
                                metadatas=batch_metas, 
                                ids=batch_ids
                            )
                            print(f"  ↗️ Uploaded batch {i // batch_size + 1}/{ (len(items) // batch_size) + 1 }...")
                        
                        file_count += 1
                        print(f" ✅ Successfully pushed all {len(items)} documents from {filename} to Cloud!")
                        continue
            except Exception as e:
                print(f"Error parsing {filename}: {e}")
                continue

        # 2. Handle Text/PDF (Unstructured fallback)
        text = ""
        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        elif filename.endswith(".pdf"):
            text = extract_text_from_pdf(filepath)
            
        if not text.strip(): continue
        
        print(f"Crunching {filename}...")
        
        chunks = chunk_text(text)
        
        # Prepare for Chroma
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in range(len(chunks))]
        
        # Upsert in small batches if necessary, default takes large batches
        collection.upsert(documents=chunks, metadatas=metadatas, ids=ids)
        file_count += 1
        print(f" ✅ Built vectors for {len(chunks)} chunks from {filename}")
        
    if file_count == 0:
        print(f"⚠️  No valid .txt or .pdf files found in '{DATA_DIR}/' folder!")
    else:
        print(f"\n🎉 Total Vectorized Chunks Available to RAG: {collection.count()}")

if __name__ == "__main__":
    ingest_data()
