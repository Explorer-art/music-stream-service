from sqlalchemy import exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import *
from config import *

@connection
async def exists_track(session: AsyncSession, track_id):
	result = await session.scalar(select(exists().where(Track.id == track_id)))

	return result

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
async def add_track(session: AsyncSession, track_id=None, title=None, artist=None, duration=None, sha256_hash=None):
	if track_id:
		track = Track(
			id=track_id,
			title = title,
			artist = artist,
			duration = duration,
			sha256_hash = sha256_hash
			)
	else:
		track = Track(
			title = title,
			artist = artist,
			duration = duration,
			sha256_hash = sha256_hash
			)

	session.add(track)
	await session.commit()
	await session.refresh(track)
	return track.id

@connection
async def update_track(session: AsyncSession, track_id, id=None, title=None, artist=None, duration=None, sha256_hash=None):
	if not await exists_track(track_id):
		return False

	track = await get_track(track_id)

	if id is not None:
		track.id = id
	if title is not None:
		track.title = title
	if artist is not None:
		track.artist = artist
	if duration is not None:
		track.duration = duration
	if sha256_hash is not None:
		track.sha256_hash = sha256_hash

	session.add(track)
	await session.commit()
	return True

@connection
async def delete_track(session: AsyncSession, track_id):
	track = await session.scalar(select(Track).filter(Track.id == track_id))

	if track is None:
		return False

	await session.delete(track)
	await session.commit()
	return True

@connection
async def search_tracks(session: AsyncSession, query):
	stmt = select(Track).filter(Track.title.ilike(f"%{query}%") | Track.title.ilike(f"%{query}%"))
	results = await session.execute(stmt)
	tracks = results.scalars().all()

	return tracks

@connection
async def exists_ptrack(session: AsyncSession, track_id):
	result = await session.scalar(select(exists().where(TrackPending.id == track_id)))

	return result

@connection
async def exists_ptrack_by_download_url(session: AsyncSession, download_url):
	result = await session.scalar(select(exists().where(TrackPending.download_url == download_url)))

	return result

@connection
async def exists_ptrack_by_image_url(session: AsyncSession, image_url):
	result = await session.scalar(select(exists().where(TrackPending.image_url == image_url)))

	return result

@connection
async def get_ptrack(session: AsyncSession, track_id):
	track = await session.scalar(select(TrackPending).filter(TrackPending.id == track_id))
	return track

@connection
async def get_ptrack_by_download_url(session: AsyncSession, download_url):
	track = await session.scalar(select(TrackPending).filter(TrackPending.download_url == download_url))
	return track

@connection
async def get_ptracks(session: AsyncSession, offset: int = 0, page_size: int = PAGE_SIZE):
	tracks = await session.scalars(select(TrackPending).offset(offset).limit(page_size))
	return tracks

@connection
async def add_ptrack(session: AsyncSession, track_id=None, title=None, artist=None, duration=None, source=None, image_url=None, download_url=None):
	if track_id:
		track = TrackPending(
			id=track_id,
			title = title,
			artist = artist,
			duration = duration,
			source = source,
			image_url = image_url,
			download_url = download_url
			)
	else:
		track = TrackPending(
			title = title,
			artist = artist,
			duration = duration,
			source = source,
			image_url = image_url,
			download_url = download_url
			)

	session.add(track)
	await session.commit()
	await session.refresh(track)
	return track.id

@connection
async def update_ptrack(session: AsyncSession, track_id, id=None, title=None, artist=None, duration=None, source=None, image_url=None, download_url=None):
	if not await exists_ptrack(track_id):
		return False

	track = await get_ptrack(track_id)

	if id is not None:
		track.id = id
	if title is not None:
		track.title = title
	if artist is not None:
		track.artist = artist
	if duration is not None:
		track.duration = duration
	if source is not None:
		track.source = source
	if image_url is not None:
		track.image_url = image_url
	if download_url is not None:
		track.download_url = download_url

	session.add(track)
	await session.commit()
	return True

@connection
async def delete_ptrack(session: AsyncSession, track_id):
	track = await session.scalar(select(TrackPending).filter(TrackPending.id == track_id))

	if track is None:
		return False

	await session.delete(track)
	await session.commit()
	return True

@connection
async def search_ptracks(session: AsyncSession, query):
	stmt = select(TrackPending)

	stmt = stmt.filter(
		(TrackPending.title.ilike(f"%{query}%")) | (TrackPending.artist.ilike(f"%{query}%"))
	)

	tracks = await session.scalars(stmt)

	return tracks