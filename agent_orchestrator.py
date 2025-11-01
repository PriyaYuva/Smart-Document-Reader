import os
import sqlite3
from ocr_utils import extract_text_from_file
from extractor import extract_fields
from database import init_db, save_document
from rag_utils import build_vector_index, query_vector_index


init_db()

def orchestrate_pipeline(file_path: str):
    print("🧠 Starting AI Orchestration Pipeline...")
    print(f"📄 Input File: {file_path}")

    
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    print("👁️  Vision Agent: Extracting text from document...")
    text = extract_text_from_file(file_bytes, file_path)
    print(f"✅ Extracted {len(text)} characters of text.\n")

    
    print("💬  Language Agent: Extracting structured fields...")
    result, meta = extract_fields(text)
    print("✅ Extracted Fields:")
    print(result, "\n")

    
    print("💾  Memory Agent: Saving document to database...")
    doc_id = save_document(os.path.basename(file_path), text, result, meta)
    print(f"✅ Document saved with ID: {doc_id}\n")


    print("🔍  Retrieval Agent: Building FAISS semantic index...")
    conn = sqlite3.connect("documents.db")
    c = conn.cursor()
    c.execute("SELECT text FROM docs")
    docs = [r[0] for r in c.fetchall()]
    conn.close()

    index, model, corpus = build_vector_index(docs)
    query = "find verified statements"
    print(f"💭  Query: {query}")
    results = query_vector_index(index, model, query, corpus, top_k=1)
    print("✅  Top Retrieved Document Snippet:")
    print(results[0][:300].replace("\n", " ") + "...")
    print("\n🏁 Pipeline completed successfully.\n")


if __name__ == "__main__":
    sample_pdf = "sample.pdf"
    if not os.path.exists(sample_pdf):
        print("⚠️ sample.pdf not found. Run generate_sample_pdf.py first.")
    else:
        orchestrate_pipeline(sample_pdf)