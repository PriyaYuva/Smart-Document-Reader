import io
import json
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from ocr_utils import extract_text_from_file
from extra import extract_fields
from database import init_db, save_document

app = FastAPI(title="Smart Document Reader - HaiIntel Task A")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn")
init_db()


@app.get("/")
def health():
    return {"status": "ok", "service": "Smart Document Reader"}


@app.post("/api/verify")
async def verify(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="File not provided.")
    filename = file.filename
    content = await file.read()
    try:
        text = extract_text_from_file(content, filename)
    except Exception as e:
        logger.exception("OCR failed")
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

    # 👇 these lines must NOT be inside the `except` block
    result, meta = extract_fields(text)
    doc_id = save_document(filename, text, result, meta)

    response = {
        "id": doc_id,
        "fileName": filename,
        "extracted": result,
        "meta": meta
    }
    return JSONResponse(content=response)
