import eyed3
import hashlib
import aiohttp
import io
from PIL import Image
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

def stream_audio_file(filename, chunk_size = 1024):
	with open(filename, "rb") as file:
		while chunk := file.read(chunk_size):
			yield chunk

async def proxy_stream_audio_file(download_url, chunk_size = 1024 * 1024):
	async with aiohttp.ClientSession() as session:
		async with session.get(download_url) as response:
			if response.status != 200:
				raise HTTPException(detail="Trasmission error", status_code=500)

			while chunk := await response.content.read(chunk_size):
				yield chunk