from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.future import select
from sqlalchemy.ext.declarative import declarative_base
from config import *

Base = declarative_base()

class User(Base):
	__tablename__ = "Users"

	id = Column(Integer, primary_key=True, autoincrement=True)
	username = Column(String, unique=True, nullable=False)
	email = Column(String, unique=True, nullable=False)
	password = Column(String, nullable=False)

class Track(Base):
	__tablename__ = "Tracks"

	id = Column(Integer, primary_key=True, autoincrement=True)
	title = Column(String)
	artist = Column(String)

class Favorite(Base):
	__tablename__ = "Favorites"

	user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"), primary_key=True)
	track_id = Column(Integer, ForeignKey("Tracks.id", ondelete="CASCADE"), primary_key=True)

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

def connection(method):
	async def wrapper(*args, **kwargs):
		async with async_session_maker() as session:
			try:
				return await method(*args, session=session, **kwargs)
			except Exception as e:
				await session.rollback()
				raise e
			finally:
				await session.close()

	return wrapper

@connection
async def exists_track(session: AsyncSession, track_id):
	track = session.scalar(select(Track).filter(Track.id == track_id)).first()

	if track is None:
		return False

	return True

@connection
async def get_track(session: AsyncSession, track_id):
	track = session.scalar(select(Track).filter(Track.id == track_id)).first()
	return track

@connection
async def get_tracks(session: AsyncSession):
	tracks = session.scalar(select(Track).filter(Track.id == track_id)).all()
	return tracks

@connection
async def add_track(session: AsyncSession, title, artist):
	track = Track(title=title, artist=artist)
	session.add(track)
	await session.commit()
	return track.id

@connection
async def delete_track(session: AsyncSession, track_id):
	track = session.scalar(select(Track).filter(Track.id == track_id)).first()

	if track is None:
		return False

	session.delete(track)
	await session.commit()
	return True