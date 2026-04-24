from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from sqlalchemy.orm import Session
from app.services.rewards_service import credit_points, get_balance, get_transactions, withdraw_points
from app.services.user_sync import get_current_user

router = APIRouter(prefix="/api/v1/rewards", tags=["rewards"])

@router.post("/credit/{points}")
def credit(points: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(401, "Auth required")
    res = credit_points(db, str(user.id), points, reason="manual_credit")
    return {"success": True, "balance": res}

@router.get("/balance")
def balance(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(401, "Auth required")
    return get_balance(db, str(user.id))


@router.get("/transactions")
def transactions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(401, "Auth required")
    txs = get_transactions(db, str(user.id))
    return {"transactions": [
        {"id": t.id, "points": t.points, "reason": t.reason, "created_at": t.created_at}
        for t in txs
    ]}


@router.post("/withdraw/{points}")
def withdraw(points: int, destination: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(401, "Auth required")
    try:
        res = withdraw_points(db, str(user.id), points, destination)
        return {"success": True, "result": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
