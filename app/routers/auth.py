from fastapi import APIRouter, HTTPException, status, Depends, Header
from app.schemas import UserCreate, Token, UserOut
from app.database import database
from app.models import users
from app.auth import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    query = users.select().where(users.c.username == user.username)
    existing = await database.fetch_one(query)
    if existing:
        raise HTTPException(status_code=400, detail="username already registered")
    hashed = get_password_hash(user.password)
    insert = users.insert().values(username=user.username, hashed_password=hashed)
    user_id = await database.execute(insert)
    token = create_access_token({"sub": str(user_id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: UserCreate):
    query = users.select().where(users.c.username == form_data.username)
    user = await database.fetch_one(query)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    token = create_access_token({"sub": str(user["id"])})
    return {"access_token": token, "token_type": "bearer"}
