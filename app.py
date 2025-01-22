import os
import random
from fastapi import Request, HTTPException
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, JSONResponse
from io import BytesIO
from database import *
from manager import *
from utils.utils import *
from config import *

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
	if not os.path.exists("db"):
		os.mkdir("db")

	if not os.path.exists(MUSIC_DIR):
		os.mkdir(MUSIC_DIR)

	if not os.path.exists(ALBUMS_DIR):
		os.mkdir(ALBUMS_DIR)

	await init_db()

@app.get("/")
async def home(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin")
async def admin_panel(request: Request):
	return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/api/tracks/upload")
async def upload_track(file: UploadFile = File(...)):
	file_content = await file.read()
	tmp_filename = str(random.randint(1, 9999999999)) + ".mp3"

	with open(f"tmp/{tmp_filename}", "wb") as file:
		file.write(file_content)

	audio_file = eyed3.load(f"tmp/{tmp_filename}")
	title = audio_file.tag.title
	artist = audio_file.tag.artist
	duration = audio_file.info.time_secs
	minutes = int(duration // 60)
	seconds = int(duration % 60)
	track_sha256_hash = get_sha256_hash_file(f"tmp/{tmp_filename}")

	if await exists_track(track_sha256_hash):
		os.remove(f"tmp/{tmp_filename}")

		raise HTTPException(detail="Track already added", status_code=400)

	track_id = await add_track(title, artist, f"{minutes:02}:{seconds:02}", track_sha256_hash)

	os.remove(f"tmp/{tmp_filename}")

	with open(f"{MUSIC_DIR}/{track_id}.mp3", "wb") as file:
		file.write(file_content)

	add_track_album(f"{MUSIC_DIR}/{track_id}.mp3")

	return JSONResponse({"message": "Track added successfully", "track_id": track_id})

@app.delete("/api/tracks/{track_id}")
async def delete_track(track_id: int):
	return JSONResponse({"message": "Track deleted"})

@app.get("/api/albums/{track_id}")
async def get_track_album():
	if not os.path.exists(f"{ALBUMS_DIR}/{track_id}.jpg"):
		return JSONResponse({"message": "Track not found"})

	return FileResponse(f"{ALBUMS_DIR}/{track_dir}.jpg")

@app.get("/api/tracks/{track_id}/stream")
async def stream_track(track_id: int):
	return StreamingResponse(iter_audio_file(f"{MUSIC_DIR}/{track_id}.mp3"), media_type="auido/mpeg")