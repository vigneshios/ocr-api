from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "OCR Server is running 🚀"}

@app.post("/ocr/")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    text = pytesseract.image_to_string(image)

    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    candidates = []

    # Step 1: Extract all lines ending with a float (e.g., Shampoo 6.99)
    for line in lines:
        match = re.match(r"(.+?)\s+(\d+[\.,]\d{2})$", line)
        if match:
            name, price = match.groups()
            name = name.strip()
            price = price.replace(",", ".")  # Normalize comma to dot
            candidates.append((name, price))

    items = []
    summary = {"total": None, "cash": None, "change": None}

    # Step 2: Assume last 2–3 short lines are summary
    tail = candidates[-3:]
    used_indices = set()

    for i, (name, price) in enumerate(reversed(tail)):
        cleaned = re.sub(r"[^a-zA-Z0-9]", "", name.lower())
        word_count = len(name.split())

        if word_count <= 2 or len(cleaned) <= 10:
            idx = len(candidates) - 1 - i
            if summary["total"] is None:
                summary["total"] = price
                used_indices.add(idx)
            elif summary["cash"] is None:
                summary["cash"] = price
                used_indices.add(idx)
            elif summary["change"] is None:
                summary["change"] = price
                used_indices.add(idx)

    # Step 3: Remaining = items
    for idx, (name, price) in enumerate(candidates):
        if idx in used_indices:
            continue
        items.append({"name": name.title(), "price": price})

    return {
        "items": items,
        "summary": summary
    }
