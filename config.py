import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

DATABASE_URL = "sqlite+aiosqlite:///db/database.db"
MUSIC_DIR = "music"
ALBUMS_DIR = "albums"