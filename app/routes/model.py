from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from transformers import pipeline
from PIL import Image
import io

app = FastAPI()

#load the model
classifier = pipeline("image")