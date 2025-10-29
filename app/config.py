import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lumen.db")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
