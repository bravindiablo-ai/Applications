from fastapi import APIRouter

router = APIRouter()

@router.post("/moderate")
def moderate_post():
    return {"message": "Post moderated successfully"}
