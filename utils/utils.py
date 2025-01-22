import eyed3
import hashlib
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

def create_thumbnail(file_src, file_dst):
	image = Image.open(file_src)
	resized_image = image.resize((300, 300))
	resized_image.save(file_dst)

def iter_audio_file(filename, chunk_size = 1024 * 1024):
	with open(filename, "rb") as file:
		while chunk := file.read(chunk_size):
			yield chunk

def add_track_album(filename):
	audio_file = eyed3.load(filename)

	for image in audio_file.tag.images:
		with open(f"{ALBUMS_DIR}/{os.path.splitext(os.path.basename(filename))[0]}.jpg", "wb") as file:
			file.write(image.image_data)