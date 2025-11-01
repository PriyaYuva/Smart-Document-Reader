from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

def build_vector_index(texts):
    """
    texts: list[str] - corpus of document texts
    returns: (index, model, texts)
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index, model, texts

def query_vector_index(index, model, query, texts, top_k=3):
    q_emb = model.encode([query], convert_to_numpy=True)
    D, I = index.search(q_emb, top_k)
    results = []
    for idx in I[0]:
        if 0 <= idx < len(texts):
            results.append(texts[idx])
    return results