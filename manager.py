from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import *
from config import *

@connection
async def exists_track(session: AsyncSession, track_id):
	track = await session.scalar(select(Track).filter(Track.id == track_id))

	if track is None:
		return False

	return True

@connection
async def exists_track_by_hash(session: AsyncSession, track_hash):
	track = await session.scalar(select(Track).filter(Track.sha256_hash == track_hash))

	if track is None:
		return False

	return True

@connection
async def get_track(session: AsyncSession, track_id):
	track = await session.scalar(select(Track).filter(Track.id == track_id))
	return track

@connection
async def get_tracks(session: AsyncSession, offset: int = 0, page_size: int = PAGE_SIZE):
	tracks = await session.scalars(select(Track).offset(offset).limit(page_size))
	return tracks

@connection
async def add_track(session: AsyncSession, title, artist, duration, download_url, downloaded, sha256_hash):
	track = Track(
		title = title,
		artist = artist,
		duration = duration,
		download_url = download_url,
		downloaded = downloaded,
		sha256_hash = sha256_hash)

	session.add(track)
	await session.commit()
	await session.refresh(track)
	return track.id

@connection
async def delete_track(session: AsyncSession, track_id):
	track = await session.scalar(select(Track).filter(Track.id == track_id))

	if track is None:
		return False

	await session.delete(track)
	await session.commit()
	return True