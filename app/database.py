from databases import Database
from sqlalchemy import MetaData, create_engine

from app.config import DATABASE_URL

database = Database(DATABASE_URL)
metadata = MetaData()
# sync engine for table create during startup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db(app):
    """
    Ensure DB tables are present immediately and register startup/shutdown
    handlers to manage the async database connection.
    """
    # Create tables synchronously right away so tests and early requests can see them.
    metadata.create_all(engine)

    @app.on_event("startup")
    async def on_startup():
        # connect the async database
        await database.connect()

    @app.on_event("shutdown")
    async def on_shutdown():
        await database.disconnect()
