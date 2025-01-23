import os
import random
from fastapi import Request, HTTPException
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, JSONResponse
from database import *
from manager import *
from search import *
from utils.utils import *
from config import *

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

hitmo = Hitmo()

@app.on_event("startup")
async def startup():
	if not os.path.exists("db"):
		os.mkdir("db")

	if not os.path.exists(MUSIC_DIR):
		os.mkdir(MUSIC_DIR)

	if not os.path.exists(IMAGES_DIR):
		os.mkdir(IMAGES_DIR)

	if not os.path.exists(THUMBNAILS_DIR):
		os.mkdir(THUMBNAILS_DIR)

	await init_db()

@app.get("/")
async def home(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin")
async def admin_panel(request: Request):
	return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/api/tracks/search")
async def search(query: str):
	tracks = await search_tracks(query)

	if tracks is None:
		return JSONResponse({"message": "Not results"})

	tracks_data = []

	for track in tracks:
		tracks_data.append({"track_id": track.id,
			"title": track.title,
			"artist": track.artist,
			"duration": track.duration,
			"thumbnail_url": f"http://{HOST}/api/albums/thumbnails/{track.id}",
			"image_url": f"http://{HOST}/api/albums/{track.id}",
			"stream_url": f"http://{HOST}/api/tracks/{track.id}/stream",
			"track_hash": track.sha256_hash})

	tracks = hitmo.search(query)
	track_pending_data = []

	if tracks is None:
		return JSONResponse({"tracks": tracks_data, "tracks_pending": track_pending_data})

	for track in tracks:
		if not await exists_ptrack_by_download_url(track.download_url) and not await exists_ptrack_by_image_url(track.image_url):
			track_id = await add_ptrack(track.title, track.artist, track.duration, track.image_url, track.download_url)

	tracks = await search_ptracks(query)

	for track in tracks:
		track_pending_data.append({"track_id": track.id,
			"title": track.title,
			"artist": track.artist,
			"duration": track.duration,
			"image_url": track.image_url,
			"stream_url": track.download_url})

	return JSONResponse({"tracks": tracks_data, "tracks_pending": track_pending_data})

@app.post("/api/tracks/upload")
async def upload_track(file: UploadFile = File(...)):
	file_content = await file.read()
	file_size = file.file._file.tell()

	if file_size > MAX_FILE_SIZE:
		raise HTTPException(detail="The file size is too large", status_code=400)

	tmp_filename = str(random.randint(1, 9999999999)) + ".mp3"

	with open(f"tmp/{tmp_filename}", "wb") as file:
		file.write(file_content)

	audio_file = eyed3.load(f"tmp/{tmp_filename}")
	title = audio_file.tag.title
	artist = audio_file.tag.artist
	duration = audio_file.info.time_secs
	minutes = int(duration // 60)
	seconds = int(duration % 60)
	track_hash = get_sha256_hash_file(f"tmp/{tmp_filename}")

	if await exists_track_by_hash(track_hash):
		os.remove(f"tmp/{tmp_filename}")

		raise HTTPException(detail="Track already added", status_code=400)

	track_id = await add_track(title, artist, f"{minutes:02}:{seconds:02}", track_hash)

	os.remove(f"tmp/{tmp_filename}")

	with open(f"{MUSIC_DIR}/{track_id}.mp3", "wb") as file:
		file.write(file_content)

	add_track_image(f"{MUSIC_DIR}/{track_id}.mp3")
	add_track_thumbnail(f"{IMAGES_DIR}/{track_id}.jpg")

	return JSONResponse({"message": "Track added successfully", "track_id": track_id})

@app.delete("/api/tracks/{track_id}")
async def del_track(track_id: int):
	if not await exists_track(track_id):
		raise HTTPException(detail="Track not found", status_code=404)

	await delete_track(track_id)

	try:
		os.remove(f"{MUSIC_DIR}/{track_id}.mp3")
	except:
		pass

	try:
		os.remove(f"{IMAGES_DIR}/{track_id}.jpg")
	except:
		pass

	return JSONResponse({"message": "Track deleted"})

@app.get("/api/images/{track_id}")
async def get_track_album(track_id: int):
	if not os.path.exists(f"{IMAGES_DIR}/{track_id}.jpg"):
		raise HTTPException(detail="Track not found", status_code=404)

	return FileResponse(f"{IMAGES_DIR}/{track_id}.jpg")

@app.get("/api/images/thumbnails/{track_id}")
async def get_track_album(track_id: int):
	if not os.path.exists(f"{THUMBNAILS_DIR}/{track_id}_thumbnail.jpg"):
		raise HTTPException(detail="Track not found", status_code=404)

	return FileResponse(f"{THUMBNAILS_DIR}/{track_id}_thumbnail.jpg")

@app.get("/api/tracks")
async def tracks(page: int = 1, page_size: int = 32):
	if page < 1 or page_size > 32:
		raise HTTPException(detail="The page can't be less than 1", status_code=400)

	tracks_data = []
	tracks = await get_tracks((page - 1) * PAGE_SIZE, page_size)

	for track in tracks:
		tracks_data.append({"track_id": track.id,
			"title": track.title,
			"artist": track.artist,
			"duration": track.duration,
			"thumbnail_url": f"http://{HOST}/api/images/thumbnails/{track.id}",
			"image_url": f"http://{HOST}/api/images/{track.id}",
			"stream_url": f"http://{HOST}/api/tracks/{track.id}/stream",
			"track_hash": track.sha256_hash})

	return JSONResponse({"tracks": tracks_data})

@app.get("/api/tracks/{track_id}")
async def get_track_info(track_id: int):
	track = await get_track(track_id)

	return JSONResponse({"title": track.title,
		"artist": track.artist,
		"duration": track.duration,
		"thumbnail_url": f"http://{HOST}/api/images/thumbnails/{track.id}",
		"image_url": f"http://{HOST}/api/images/{track.id}",
		"stream_url": f"http://{HOST}/api/tracks/{track.id}/stream",
		"track_hash": track.sha256_hash})

@app.get("/api/tracks/{track_id}/stream")
async def stream_track(track_id: int):
	if not await exists_track(track_id):
		raise HTTPException(detail="Track not found", status_code=404)

	return StreamingResponse(stream_audio_file(f"{MUSIC_DIR}/{track_id}.mp3"), media_type="auido/mpeg")

@app.get("/api/tracks/p/{track_id}/stream")
async def stream_ptrack(track_id: int):
	if not await exists_ptrack(track_id):
		raise HTTPException(detail="Track not found", status_code=404)

	try:
		track = await get_ptrack(track_id)

		return StreamingResponse(proxy_stream_audio_file(track.download_url), media_type="audio/mpeg")
	except:
		raise HTTPException(detail="Transmission error", status_code=500)