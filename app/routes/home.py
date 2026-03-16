# app/routes/home.py

from fastapi import APIRouter, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
import os
import random

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/detect")
async def detect(request: Request, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ---- MOCK DETECTION ----
    prediction = random.uniform(0, 1)
    label = "Fake" if prediction > 0.5 else "Real"
    confidence = round(prediction * 100, 2)

    result = {
        "label": label,
        "confidence": confidence
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result
        }
    )
