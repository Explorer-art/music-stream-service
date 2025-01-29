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

def add_track_image(filename):
	audio_file = eyed3.load(filename)

	image_found = False

	for image in audio_file.tag.images:
		image_found = True

		with open(f"{IMAGES_DIR}/{os.path.splitext(os.path.basename(filename))[0]}.jpg", "wb") as file:
			file.write(image.image_data)

	return image_found

async def download_file(url, filename):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			if response.status != 200:
				raise HTTPException(detail="Trasmission error", status_code=500)

			with open(filename, "wb") as file:
				while chunk := await response.content.read(CHUNK_SIZE):
					file.write(chunk)

async def download_track(download_url, image_url, track_id):
	await download_file(download_url, f"{MUSIC_DIR}/{track_id}.mp3")
	await download_file(image_url, f"{IMAGES_DIR}/{track_id}.png")

	sha256_hash = get_sha256_hash_file(f"{MUSIC_DIR}/{track_id}.mp3")

	await update_track(track_id, sha256_hash=sha256_hash)
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