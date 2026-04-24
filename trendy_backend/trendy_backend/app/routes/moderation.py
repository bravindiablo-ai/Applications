from fastapi import APIRouter, Depends, HTTPException
from app.services.moderation_advanced import ModerationAdvanced
from app.services.user_sync import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session
from app.services.moderation_queue_service import report_item, get_pending_queue, resolve_queue_item

router = APIRouter(prefix="/api/v1/moderation", tags=["moderation"])
mod = ModerationAdvanced()

@router.post("/analyze/text")
def analyze_text(payload: dict, user=Depends(get_current_user)):
    text = payload.get("text")
    res = mod.analyze_comment(text)
    return {"ok": True, "result": res}


@router.post('/report')
def report(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """User reports an item for moderation"""
    if not user:
        raise HTTPException(401, 'Auth required')
    target_type = payload.get('target_type')
    target_id = payload.get('target_id')
    reason = payload.get('reason')
    rep = report_item(db, int(user.id), target_type, int(target_id), reason)
    return {"ok": True, "report_id": rep.id}


@router.get('/admin/queue')
def admin_queue(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not getattr(user, 'is_admin', False):
        raise HTTPException(403, 'admin only')
    items = get_pending_queue(db)
    return {"items": [ {"id": i.id, "type": i.item_type, "item_id": i.item_id, "reason": i.reason} for i in items ]}


@router.post('/admin/resolve')
def admin_resolve(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not getattr(user, 'is_admin', False):
        raise HTTPException(403, 'admin only')
    qid = payload.get('queue_id')
    resolution = payload.get('resolution', {})
    q = resolve_queue_item(db, int(qid), int(user.id), resolution)
    if not q:
        raise HTTPException(404, 'queue item not found')
    return {"ok": True, "queue_id": q.id}

@router.post("/admin/review")
def admin_review(payload: dict, user=Depends(get_current_user)):
    # simple admin guard
    if not getattr(user, "is_admin", False):
        raise HTTPException(403, "admin only")
    # payload contains id to review; stubbed
    return {"ok": True, "reviewed": payload}
