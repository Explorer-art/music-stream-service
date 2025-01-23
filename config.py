import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

HOST = "127.0.0.1:8000"
DATABASE_URL = "sqlite+aiosqlite:///db/database.db"
MUSIC_DIR = "music"
IMAGES_DIR = "images"
THUMBNAILS_DIR = "images/thumbnails"
MAX_FILE_SIZE = 10485760
PAGE_SIZE = 32