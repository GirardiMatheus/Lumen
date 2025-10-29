from sqlalchemy import Table, Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.sql import func
import enum

from app.database import metadata

class TransactionType(str, enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False),
)

accounts = Table(
    "accounts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("name", String, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("account_id", Integer, ForeignKey("accounts.id"), nullable=False),
    Column("type", Enum(TransactionType), nullable=False),
    Column("amount", Float, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
