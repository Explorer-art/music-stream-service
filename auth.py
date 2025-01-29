import os
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Union, Any
from jose import jwt, JWTError
from fastapi import Request, Depends, HTTPException, status
from passlib.context import CryptContext
from manager import *
from config import *

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
	salt = bcrypt.gensalt()
	password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)

	return password_hash

def verify_password(password: str, hashed_password) -> str:
	return password_context.verify(password, hashed_password)

async def verify_user(username, password):
	if not await exists_user_by_username(username):
		return False

	user = await get_user(username)

	if not verify_password(password, user.password):
		return False

	return user

def create_access_token(data: dict):
	to_encode = data.copy()
	expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
	to_encode.update({"exp": expire})
	encode_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

	return encode_jwt

async def get_current_user_id(token: str):
	try:
		payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=ALGORITHM)
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="The token is not valid")

	expire = payload.get("exp")
	expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)

	if (not expire) or (expire_time < datetime.now(timezone.utc)):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="The token has expired")

	user_id = payload.get("sub")

	return user_id