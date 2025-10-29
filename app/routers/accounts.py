from fastapi import APIRouter, HTTPException, status, Header, Depends
from typing import Optional, List, Dict, Any
from jose import jwt, JWTError
from app.config import SECRET_KEY, ALGORITHM
from app.database import database
from app import models
from app import schemas

router = APIRouter()

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise JWTError()
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    query = models.users.select().where(models.users.c.id == int(user_id))
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.post("/accounts", response_model=schemas.AccountOut, summary="Create account for current user")
async def create_account(payload: schemas.AccountCreate, current_user = Depends(get_current_user)):
    insert = models.accounts.insert().values(user_id=current_user["id"], name=payload.name)
    account_id = await database.execute(insert)
    q = models.accounts.select().where(models.accounts.c.id == account_id)
    row = await database.fetch_one(q)
    return row

@router.post("/accounts/{account_id}/transactions", response_model=schemas.TransactionOut, summary="Create deposit or withdrawal")
async def create_transaction(account_id: int, tx: schemas.TransactionCreate, current_user = Depends(get_current_user)):
    # verify account exists and belongs to user
    q_acc = models.accounts.select().where(models.accounts.c.id == account_id)
    account = await database.fetch_one(q_acc)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    # amount validated by schema (>0). Compute current balance
    q_txs = models.transactions.select().where(models.transactions.c.account_id == account_id)
    rows = await database.fetch_all(q_txs)
    balance = 0.0
    for r in rows:
        if r["type"] == models.TransactionType.deposit.value:
            balance += float(r["amount"])
        else:
            balance -= float(r["amount"])

    if tx.type == schemas.TransactionType.withdrawal:
        if balance < float(tx.amount):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

    # insert transaction
    ins = models.transactions.insert().values(account_id=account_id, type=tx.type.value, amount=tx.amount)
    tx_id = await database.execute(ins)
    q_tx = models.transactions.select().where(models.transactions.c.id == tx_id)
    created = await database.fetch_one(q_tx)
    return created

@router.get("/accounts/{account_id}/statement", response_model=schemas.Statement, summary="Get account statement with all transactions and balance")
async def get_statement(account_id: int, current_user = Depends(get_current_user)):
    q_acc = models.accounts.select().where(models.accounts.c.id == account_id)
    account = await database.fetch_one(q_acc)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    q_txs = models.transactions.select().where(models.transactions.c.account_id == account_id).order_by(models.transactions.c.created_at)
    tx_rows = await database.fetch_all(q_txs)
    # compute balance
    balance = 0.0
    tx_list: List[Dict[str, Any]] = []
    for r in tx_rows:
        if r["type"] == models.TransactionType.deposit.value:
            balance += float(r["amount"])
        else:
            balance -= float(r["amount"])
        tx_list.append(dict(r))

    statement = {
        "account": dict(account),
        "transactions": tx_list,
        "balance": balance
    }
    return statement
