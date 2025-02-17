from pydantic import BaseModel

class LoginRequest(BaseModel):
	username: str
	password: str

class UpdateUser(BaseModel):
	username: Optional[str]
	avatar: Optional[str]
	password: Optional[str]
	permissions_level: Optional[int]