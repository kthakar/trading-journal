from fastapi import APIRouter
from ..brokerage import tastytrade

router = APIRouter()


@router.get("/accounts")
def get_accounts():
    accounts = tastytrade.list_accounts()
    return {"accounts": accounts}
