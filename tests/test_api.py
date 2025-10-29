import sys
from pathlib import Path
import os
import pytest
from httpx import AsyncClient, ASGITransport

# Ensure the project root is in sys.path so `import app` works under pytest
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Set test DB and secret before importing the app so config/init_db uses them
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_lumen.db")
os.environ.setdefault("SECRET_KEY", "testsecretkey")

# Ensure previous test DB is removed before importing app
_db_file = Path("test_lumen.db")
if _db_file.exists():
    try:
        _db_file.unlink()
    except Exception:
        pass

from app.main import app  # import after env set so DB config is applied

@pytest.mark.asyncio
async def test_full_account_flow_and_validations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register user (returns token)
        r = await ac.post("/auth/register", json={"username": "tester", "password": "secret123"})
        assert r.status_code == 200, r.text
        token = r.json().get("access_token")
        assert token

        headers = {"Authorization": f"Bearer {token}"}

        # Create account
        r = await ac.post("/accounts", json={"name": "Conta Teste"}, headers=headers)
        assert r.status_code == 200, r.text
        acc = r.json()
        acc_id = acc["id"]

        # Deposit positive amount
        r = await ac.post(f"/accounts/{acc_id}/transactions",
                            json={"type": "deposit", "amount": 150.75}, headers=headers)
        assert r.status_code == 200, r.text
        tx1 = r.json()
        assert float(tx1["amount"]) == pytest.approx(150.75)

        # Withdraw a valid amount
        r = await ac.post(f"/accounts/{acc_id}/transactions",
                            json={"type": "withdrawal", "amount": 50.25}, headers=headers)
        assert r.status_code == 200, r.text

        # Attempt to withdraw more than balance -> should fail (400)
        r = await ac.post(f"/accounts/{acc_id}/transactions",
                            json={"type": "withdrawal", "amount": 1000}, headers=headers)
        assert r.status_code == 400

        # Attempt to create transaction with negative amount -> validation error (422)
        r = await ac.post(f"/accounts/{acc_id}/transactions",
                            json={"type": "deposit", "amount": -10}, headers=headers)
        assert r.status_code == 422

        # Get statement and verify transactions and computed balance
        r = await ac.get(f"/accounts/{acc_id}/statement", headers=headers)
        assert r.status_code == 200, r.text
        statement = r.json()
        assert statement["account"]["id"] == acc_id
        # balance should be 150.75 - 50.25 = 100.5
        assert float(statement["balance"]) == pytest.approx(100.5)
        assert len(statement["transactions"]) >= 2

    # cleanup test DB file
    if _db_file.exists():
        try:
            _db_file.unlink()
        except Exception:
            pass