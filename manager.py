from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import *

@connection
async def exists_track(session: AsyncSession, track_hash):
	track = await session.scalar(select(Track).filter(Track.sha256_hash == track_hash))

	if track is None:
		return False

	return True

@connection
async def get_track(session: AsyncSession, track_id):
	track = await session.scalar(select(Track).filter(Track.id == track_id))
	return track

@connection
async def get_tracks():
	tracks = await session.execute(select(Track).filter(Track.id == track_id)).scalars().all()
	return tracks

@connection
async def add_track(session: AsyncSession, title, artist, duration, sha256_hash):
	track = Track(
		title = title,
		artist = artist,
		duration = duration,
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

	session.delete(track)
	await session.commit()
	return True