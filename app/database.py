from databases import Database
from sqlalchemy import MetaData, create_engine

from app.config import DATABASE_URL

database = Database(DATABASE_URL)
metadata = MetaData()
# sync engine for table create during startup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db(app):
    """
    Register startup and shutdown events on the FastAPI app to create tables
    and connect/disconnect the async `database`.
    """
    @app.on_event("startup")
    async def on_startup():
        # create tables synchronously (SQLAlchemy engine)
        metadata.create_all(engine)
        # connect the async database
        await database.connect()

    @app.on_event("shutdown")
    async def on_shutdown():
        await database.disconnect()
