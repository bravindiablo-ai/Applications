from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging
from app.database import get_db
from app.models.post import Post
# from app.models.comment import Comment  # Comment model not found, commenting out for now
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse
from app.ai.moderation import detect_offensive_content

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    # AI moderation
    if detect_offensive_content(post.content):
        raise HTTPException(status_code=400, detail="Content flagged as inappropriate by AI.")
    # Ensure a valid user exists
    user = db.query(User).first()
    if not user:
        user = User(email="demo@trendy.app", username="demo", password="demo")
        db.add(user)
        db.commit()
        db.refresh(user)

    new_post = Post(
        user_id=user.id,
        content=post.content,
        image_url=post.image_url
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/", response_model=list[dict])
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    result = []
    for p in posts:
        result.append({
            "id": p.id,
            "content": p.content,
            "imageUrl": p.image_url,
            "createdAt": p.created_at.isoformat() if p.created_at else None,
            "likes": p.likes_count or 0,
            "comments": len(p.comments) if p.comments is not None else 0,
            "username": p.user.username if p.user else "unknown",
            "userPhoto": p.user.avatar_url if p.user and hasattr(p.user, "avatar_url") else None,
        })
    return result

@router.get("/all", response_model=list[PostResponse])
def get_all_posts(db: Session = Depends(get_db)):
    return db.query(Post).order_by(Post.created_at.desc()).all()

@router.get("/me", response_model=list[PostResponse])
def get_my_posts(db: Session = Depends(get_db), user_id: int = 1):
    return db.query(Post).filter(Post.user_id == user_id).all()

@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return {"msg": "Post deleted"}

@router.post("/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.likes_count = (post.likes_count or 0) + 1
    db.commit()
    return {"message": "Post liked"}

@router.delete("/{post_id}/unlike")
def unlike_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.likes_count = max(0, (post.likes_count or 0) - 1)
    db.commit()
    return {"message": "Post unliked"}

# @router.post("/{post_id}/comments", status_code=status.HTTP_201_CREATED)
# def add_comment(post_id: int, request: dict, db: Session = Depends(get_db)):
#     post = db.query(Post).filter(Post.id == post_id).first()
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
#     content = request.get("content") or request.get("text")
#     if not content:
#         raise HTTPException(status_code=400, detail="Missing comment content")
#     # Ensure an owner user exists
#     user = db.query(User).first()
#     if not user:
#         user = User(email="demo@trendy.app", username="demo", password="demo")
#        db.add(user)
#        db.commit()
#        db.refresh(user)
#     comment = Comment(text=content, post_id=post.id, owner_id=user.id)
#     db.add(comment)
#     db.commit()
#     return {"id": comment.id, "content": comment.text}

@router.get("/welcome")
def welcome(request: Request):
    """
    Returns a welcome message and logs request metadata.
    """
    logger.info(f"Request received: {request.method} {request.url.path}")
    return {"message": "Welcome to the TRENDY API Service!"}
