import eyed3
import hashlib
import aiohttp
import io
from PIL import Image
from manager import *
from config import *

def get_sha256_hash_file(filename):
	sha256 = hashlib.new("sha256")

	with open(filename, "rb") as file:
		while True:
			data = file.read(1024)

			if not data:
				break

			sha256.update(data)

	return sha256.hexdigest()

def add_track_thumbnail(filename):
	image = Image.open(filename)
	resized_image = image.resize((300, 300))
	resized_image.save(f"{THUMBNAILS_DIR}/{os.path.splitext(os.path.basename(filename))[0]}.jpg")

def add_track_image(filename):
	audio_file = eyed3.load(filename)

	image_found = False

	for image in audio_file.tag.images:
		image_found = True

		with open(f"{IMAGES_DIR}/{os.path.splitext(os.path.basename(filename))[0]}.jpg", "wb") as file:
			file.write(image.image_data)

	return image_found

async def download_track(url, track_id):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			if response.status != 200:
				raise HTTPException(detail="Trasmission error", status_code=500)

			with open(f"{MUSIC_DIR}/{track_id}.mp3", "wb") as file:
				while chunk := await response.content.read(CHUNK_SIZE):
					file.write(chunk)

	await update_track(track_id, sha256_hash=get_sha256_hash_file(f"{MUSIC_DIR}/{track_id}.mp3"))
	await delete_ptrack(track_id)

def stream_audio_file(filename):
	with open(filename, "rb") as file:
		while chunk := file.read(CHUNK_SIZE):
			yield chunk

async def proxy_stream_audio_file(download_url):
	async with aiohttp.ClientSession() as session:
		async with session.get(download_url) as response:
			if response.status != 200:
				raise HTTPException(detail="Trasmission error", status_code=500)

			while chunk := await response.content.read(CHUNK_SIZE):
				yield chunk