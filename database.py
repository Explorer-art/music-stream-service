from sqlalchemy import Column, Integer, String, Boolean, Sequence
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import DATABASE_URL

track_id_seq = Sequence("track_id_seq", start=1, increment=1)

class Base(DeclarativeBase):
	pass

class Track(Base):
	__tablename__ = "Tracks"

	id = Column(Integer, track_id_seq, primary_key=True)
	title = Column(String)
	artist = Column(String)
	duration = Column(String)
	sha256_hash = Column(String, unique=True)

class TrackPending(Base):
	__tablename__ = "TracksPending"

	id = Column(Integer, track_id_seq, primary_key=True)
	title = Column(String)
	artist = Column(String)
	duration = Column(String)
	image_url = Column(String, unique=True)
	download_url = Column(String, unique=True)

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

def connection(func):
	async def wrapper(*args, **kwargs):
		async with AsyncSessionLocal() as session:
			return await func(session, *args, **kwargs)

	return wrapper