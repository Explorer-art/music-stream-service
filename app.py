import os
from fastapi import Request
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, JSONResponse
from io import BytesIO
from init import init
from database import *
from utils.utils import *
from config import *

init()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin")
async def admin_panel(request: Request):
	return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/api/tracks/upload")
async def add_track(file: UploadFile = File(...)):
	file_content = await file.read()
	audio_file = eyed3.load(BytesIO(file_content))
	track_id = add_track(audio_file.tag.title, audio_file.tag.artist)

	with open(f"{MUSIC_DIR}/{track_id}.mp3", "wb") as file:
		file.write(file_content)

	add_track_album(f"{MUSIC_DIR}/{track_id}.mp3")

	return JSONResponse({"message": "Track added successfully", "track_id": track_id})

@app.post("/api/tracks/upload")
async def delete_track(track_id: int = Form(...)):
	return JSONResponse({"message": "Track deleted"})

@app.get("/api/albums/{track_id}")
async def get_track_album(track_id: str):
	if not os.path.exists(f"{ALBUMS_DIR}/{track_id}.jpg"):
		return JSONResponse({"message": "Track not found"})

	return FileResponse(f"{ALBUMS_DIR}/{track_dir}.jpg")

@app.get("/api/tracks/{track_id}/stream")
async def stream_track(track_id: int):
	return StreamingResponse(iter_audio_file(f"{MUSIC_DIR}/{track_id}.mp3"), media_type="auido/mpeg")