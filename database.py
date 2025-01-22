from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import DATABASE_URL

class Base(DeclarativeBase):
	pass

class Track(Base):
	__tablename__ = "Tracks"

	id = Column(Integer, primary_key=True, autoincrement=True)
	title = Column(String)
	artist = Column(String)
	duration = Column(String)
	download_url = Column(String)
	downloaded = Column(Boolean)
	sha256_hash = Column(String, unique=True, nullable=False)

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