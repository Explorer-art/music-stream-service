import eyed3
from config import *

def iter_audio_file(filename, chunk_size = 1024 * 1024):
	with open(filename, "rb") as file:
		while chunk := file.read(chunk_size):
			yield chunk

def add_track_album(filename):
	audio_file = eyed3.load(filename)

	for image in audio_file.tag.images:
		with open(f"{ALBUMS_DIR}/{track_id}.jpg") as file:
			file.write(image.image_data)