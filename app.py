import os
import random
import asyncio
from fastapi import FastAPI, Request, Response, Header, Cookie, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, JSONResponse
from passlib.context import CryptContext
from database import *
from manager import *
from auth import *
from schemes import *
from search import *
from utils.utils import *
from config import *

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

hitmo = Hitmo()

async def verify_user(username, password):
	if not await exists_user_by_username(username):
		return False

	user = await get_user_by_username(username)

	if not password_context.verify(password, user.password):
		return False

	return user

async def get_current_user(token):
	if not token:
		raise HTTPException(detail="Unauthorized", status_code=401)

	user_id = await get_current_user_id(token)

	user = await get_user(int(user_id))

	if user is None:
		raise HTTPException(detail="Unauthorized", status_code=401)

	return user

@app.on_event("startup")
async def startup():
	if not os.path.exists(MUSIC_DIR):
		os.mkdir(MUSIC_DIR)

	if not os.path.exists(IMAGES_DIR):
		os.mkdir(IMAGES_DIR)

	await init_db()

@app.get("/")
async def home_page(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
	return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin")
async def admin_panel(request: Request, user_access_token: str = Cookie(None)):
	user = await get_current_user(user_access_token)

	print(user.permissions_level)

	if user.permissions_level > 0:
		return JSONResponse({"message": "Access denied"}, status_code=403)

	return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/api/login")
async def login(username = Form(...), password = Form(...)):
	check = await verify_user(username, password)

	if not check:
		return JSONResponse({"message": "Wrong username or password"}, status_code=401)

	token = create_access_token({"sub": str(check.id)})
	return JSONResponse({"token": token})

@app.post("/api/tracks/upload")
async def upload_track(file: UploadFile = File(...), authorization: str = Header(None)):
	user = await get_current_user(authorization)

	file_content = await file.read()
	file_size = file.file._file.tell()

	if file_size > MAX_FILE_SIZE:
		raise HTTPException(detail="The file size is too large", status_code=400)

	tmp_filename = str(random.randint(1, 9999999999)) + ".mp3"

	with open(f"tmp/{tmp_filename}", "wb") as file:
		file.write(file_content)

	audio_file = eyed3.load(f"tmp/{tmp_filename}")
	title = audio_file.tag.title if audio_file.tag.title else "Unknown title"
	artist = audio_file.tag.artist if audio_file.tag.artist else "Unknown artist"
	duration = audio_file.info.time_secs
	minutes = int(duration // 60)
	seconds = int(duration % 60)
	track_hash = get_sha256_hash_file(f"tmp/{tmp_filename}")

	if await exists_track_by_hash(track_hash):
		os.remove(f"tmp/{tmp_filename}")

		raise HTTPException(detail="Track already added", status_code=400)

	track_id = await add_track(
		title=title,
		artist=artist,
		duration=f"{minutes:02}:{seconds:02}",
		sha256_hash=track_hash
		)

	os.remove(f"tmp/{tmp_filename}")

	with open(f"{MUSIC_DIR}/{track_id}.mp3", "wb") as file:
		file.write(file_content)

	add_track_image(f"{MUSIC_DIR}/{track_id}.mp3")

	return JSONResponse({"message": "Track added successfully", "track_id": track_id})

@app.delete("/api/tracks/{track_id}")
async def del_track(track_id: int, authorization: str = Header(None)):
	user = await get_current_user(authorization)

	if await exists_track(track_id):
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
	elif await exists_ptrack(track_id):
		await delete_ptrack(track_id)

		return JSONResponse({"message": "Track deleted"})
	else:
		raise HTTPException(detail="Track not found", status_code=404)

@app.get("/api/tracks/search")
async def search(query: str, authorization: str = Header(None)):
	user = await get_current_user(authorization)

	tracks = await search_tracks(query)

	if tracks is None:
		return JSONResponse({"message": "Not results"})

	tracks_data = []

	for track in tracks:
		tracks_data.append({"track_id": track.id,
			"title": track.title,
			"artist": track.artist,
			"duration": track.duration,
			"image_url": f"http://{HOST}/api/tracks/{track.id}/image",
			"stream_url": f"http://{HOST}/api/tracks/{track.id}/stream"})

	if GLOBAL_SEARCH:
		tracks = hitmo.search(query)

		if tracks is None:
			return JSONResponse({"tracks": tracks_data})

		for track in tracks:
			if not await exists_ptrack_by_download_url(track.download_url):
				track_id = await add_ptrack(title=track.title,
					artist=track.artist,
					duration=track.duration,
					source = "Hitmo",
					image_url=track.image_url,
					download_url=track.download_url
					)

			track = await get_ptrack_by_download_url(track.download_url)

			tracks_data.append({"track_id": track.id,
				"title": track.title,
				"artist": track.artist,
				"duration": track.duration,
				"image_url": f"http://{HOST}/api/tracks/{track.id}/image",
				"stream_url": f"http://{HOST}/api/tracks/{track.id}/stream"})

	return JSONResponse({"tracks": tracks_data})

@app.get("/api/tracks")
async def tracks(page: int = 1, page_size: int = 32, authorization: str = Header(None)):
	user = await get_current_user(authorization)

	if page < 1 or page_size > 32:
		raise HTTPException(detail="The page can't be less than 1", status_code=400)

	tracks_data = []
	tracks = await get_tracks((page - 1) * PAGE_SIZE, page_size)

	for track in tracks:
		tracks_data.append({"track_id": track.id,
			"title": track.title,
			"artist": track.artist,
			"duration": track.duration,
			"image_url": f"http://{HOST}/api/tracks/{track.id}/image",
			"stream_url": f"http://{HOST}/api/tracks/{track.id}/stream",
			"track_hash": track.sha256_hash})

	return JSONResponse({"tracks": tracks_data})

@app.get("/api/tracks/{track_id}")
async def get_track_info(track_id: int):
	if await exists_track(track_id):
		track = await get_track(track_id)

		return JSONResponse({"title": track.title,
			"artist": track.artist,
			"duration": track.duration,
			"image_url": f"http://{HOST}/api/tracks/{track.id}/image",
			"stream_url": f"http://{HOST}/api/tracks/{track.id}/stream"})
	elif await exists_ptrack(track_id) and GLOBAL_SEARCH:
		track = await get_ptrack(tracK_id)

		return JSONResponse({"title": track.title,
			"artist": track.artist,
			"duration": track.duration,
			"image_url": f"http://{HOST}/api/tracks/{track.id}/image",
			"stream_url": f"http://{HOST}/api/tracks/{track.id}/stream"})
	else:
		raise HTTPException(detail="Track not found", status_code=404)

@app.get("/api/tracks/{track_id}/image")
async def get_track_image(track_id: int):
	if await exists_track(track_id):
		if not os.path.exists(f"{IMAGES_DIR}/{track_id}.png"):
			raise HTTPException(detail="Track not found", status_code=404)

		return FileResponse(f"{IMAGES_DIR}/{track_id}.png")
	elif await exists_ptrack(track_id) and GLOBAL_SEARCH:
		track = await get_ptrack(track_id)

		return RedirectResponse(url=track.image_url)
	else:
		raise HTTPException(detail="Track not found", status_code=404)

@app.get("/api/tracks/{track_id}/stream")
async def stream_track(track_id: int):
	if await exists_track(track_id) and not await exists_ptrack(track_id):
		return StreamingResponse(stream_audio_file(f"{MUSIC_DIR}/{track_id}.mp3"), media_type="auido/mpeg")
	elif await exists_ptrack(track_id) and GLOBAL_SEARCH:
		track = await get_ptrack(track_id)

		if not await exists_track(track_id):
			track_id = await add_track(
				track_id=track.id,
				title=track.title,
				artist=track.artist,
				duration=track.duration,
				sha256_hash=""
				)

			asyncio.create_task(download_track(track.download_url, track.image_url, track.id))

		return StreamingResponse(proxy_stream_audio_file(track.download_url), media_type="audio/mpeg")
	else:
		raise HTTPException(detail="Track not found", status_code=404)