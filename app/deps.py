from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from app.config import SECRET_KEY, ALGORITHM
from app.database import database
from app import models

async def get_current_user(token: str = Depends(lambda: None), authorization: str = None, token_header: str = Depends(lambda: None)):
    # FastAPI will provide token via dependency; but to keep simple, extract from Authorization header
    raise RuntimeError("This function is replaced by router-specific dependency")
