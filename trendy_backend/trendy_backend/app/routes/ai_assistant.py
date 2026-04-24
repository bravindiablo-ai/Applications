from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.ai_assistant import AIRecommendationsAssistant
from app.database import get_db

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

class Query(BaseModel):
    prompt: str
    limit: int = 10

@router.post("/recommend")
def recommend(payload: Query, db=Depends(get_db), user=None):
    assistant = AIRecommendationsAssistant(db=db)
    return assistant.generate_recommendations(payload.prompt, user_id=getattr(user, "id", None), limit=payload.limit)
