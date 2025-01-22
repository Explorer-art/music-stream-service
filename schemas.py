from pydantic import BaseModel

class AddTrack(BaseModel):
	title: str
	description: str