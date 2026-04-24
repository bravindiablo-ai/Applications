from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.follower import Follower
from app.auth.middleware import get_current_user_id

router = APIRouter(prefix="/users", tags=["Followers"])

@router.post("/{user_id}/follow")
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Follow a user"""
    if user_id == current_user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    existing_follow = db.query(Follower).filter(
        Follower.follower_id == current_user_id,
        Follower.followed_id == user_id
    ).first()
    
    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    # Create follow relationship
    follow = Follower(
        follower_id=current_user_id,
        followed_id=user_id
    )
    db.add(follow)
    db.commit()
    
    # Update follower/following counts
    user.followers_count += 1
    follower_user = db.query(User).filter(User.id == current_user_id).first()
    follower_user.following_count += 1
    db.commit()
    
    return {"message": "Successfully followed user"}

@router.delete("/{user_id}/unfollow")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Unfollow a user"""
    follow = db.query(Follower).filter(
        Follower.follower_id == current_user_id,
        Follower.followed_id == user_id
    ).first()
    
    if not follow:
        raise HTTPException(status_code=400, detail="Not following this user")
    
    db.delete(follow)
    db.commit()
    
    # Update follower/following counts
    user = db.query(User).filter(User.id == user_id).first()
    user.followers_count -= 1
    follower_user = db.query(User).filter(User.id == current_user_id).first()
    follower_user.following_count -= 1
    db.commit()
    
    return {"message": "Successfully unfollowed user"}

@router.get("/{user_id}/followers")
def get_followers(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get followers of a user"""
    followers = db.query(User).join(Follower, Follower.follower_id == User.id).filter(
        Follower.followed_id == user_id
    ).all()
    
    return {
        "followers": [
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url
            }
            for user in followers
        ],
        "count": len(followers)
    }

@router.get("/{user_id}/following")
def get_following(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get users that a user is following"""
    following = db.query(User).join(Follower, Follower.followed_id == User.id).filter(
        Follower.follower_id == user_id
    ).all()
    
    return {
        "following": [
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url
            }
            for user in following
        ],
        "count": len(following)
    }

@router.get("/{user_id}/is_following/{target_user_id}")
def is_following(
    user_id: int,
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Check if current user is following target user"""
    follow = db.query(Follower).filter(
        Follower.follower_id == current_user_id,
        Follower.followed_id == target_user_id
    ).first()
    
    return {"is_following": follow is not None}

@router.get("/{user_id}/stats")
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "followers_count": user.followers_count,
        "following_count": user.following_count,
        "posts_count": user.posts_count
    }

@router.get("/search")
def search_users(
    query: str,
    db: Session = Depends(get_db)
):
    """Search users by username or email"""
    users = db.query(User).filter(
        (User.username.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))
    ).limit(20).all()
    
    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url
            }
            for user in users
        ],
        "count": len(users)
    }
