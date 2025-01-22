import os
from database import *
from config import *

def init():
	if not os.path.exists("db"):
		os.mkdir("db")

	if not os.path.exists(MUSIC_DIR):
		os.mkdir(MUSIC_DIR)

	if not os.path.exists(ALBUMS_DIR):
		os.mkdir(ALBUMS_DIR)

	init_db()