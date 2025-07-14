from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
import io

app = FastAPI()

@app.get("/")
def home():
    return {"message": "OCR Server is running 🚀"}

@app.post("/ocr/")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # OCR using pytesseract
    text = pytesseract.image_to_string(image)

    return JSONResponse(content={"extracted_text": text})
