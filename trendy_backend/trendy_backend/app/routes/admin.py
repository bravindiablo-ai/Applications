from fastapi import APIRouter, Depends, HTTPException
from app.services.user_sync import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/health")
def health(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not getattr(user, "is_admin", False):
        raise HTTPException(403, "admin only")
    return {"ok": True, "status": "healthy"}
