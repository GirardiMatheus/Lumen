from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: int
    username: str

class AccountCreate(BaseModel):
    name: str = Field(..., min_length=1)

class AccountOut(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime

class TransactionType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"

class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float

    @validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be positive")
        return v

class TransactionOut(BaseModel):
    id: int
    account_id: int
    type: TransactionType
    amount: float
    created_at: datetime

class Statement(BaseModel):
    account: AccountOut
    transactions: List[TransactionOut]
    balance: float
