import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

HOST = "127.0.0.1:8000"
DATABASE_URL = "postgresql+asyncpg://admin:password@localhost:5432/music"
MUSIC_DIR = "tracks"
IMAGES_DIR = "images"
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
GLOBAL_SEARCH = True
MAX_FILE_SIZE = 10485760
PAGE_SIZE = 32
CHUNK_SIZE = 1024