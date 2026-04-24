"""
User Relationships Routes for TRENDY App
Handles following, blocking, muting, and user interactions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user_relationships import UserRelationship, UserBlock, UserMute, RelationshipType
from app.models.user import User
from app.auth.middleware import get_current_user

router = APIRouter(prefix="/users", tags=["user-relationships"])

class FollowRequest(BaseModel):
    following_id: int
    relationship_type: Optional[RelationshipType] = RelationshipType.FOLLOWING
    notification_enabled: Optional[bool] = True

class BlockRequest(BaseModel):
    blocked_id: int
    reason: Optional[str] = None
    is_permanent: Optional[bool] = False

class MuteRequest(BaseModel):
    muted_id: int
    mute_stories: Optional[bool] = True
    mute_posts: Optional[bool] = True
    mute_comments: Optional[bool] = False
    mute_messages: Optional[bool] = False

@router.post("/follow", summary="Follow another user")
async def follow_user(
    request: FollowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Follow another user
    """
    try:
        # Check if user exists
        target_user = db.query(User).filter(User.id == request.following_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already following
        existing_relationship = db.query(UserRelationship).filter(
            UserRelationship.follower_id == current_user.id,
            UserRelationship.following_id == request.following_id
        ).first()
        
        if existing_relationship:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already following this user"
            )
        
        # Create new relationship
        relationship = UserRelationship(
            follower_id=current_user.id,
            following_id=request.following_id,
            relationship_type=request.relationship_type,
            notification_enabled=request.notification_enabled
        )
        
        db.add(relationship)
        db.commit()
        
        return {"message": "Successfully followed user", "relationship_id": relationship.id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to follow user: {str(e)}"
        )

@router.delete("/unfollow/{user_id}", summary="Unfollow a user")
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unfollow a user
    """
    try:
        relationship = db.query(UserRelationship).filter(
            UserRelationship.follower_id == current_user.id,
            UserRelationship.following_id == user_id
        ).first()
        
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not following this user"
            )
        
        db.delete(relationship)
        db.commit()
        
        return {"message": "Successfully unfollowed user"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unfollow user: {str(e)}"
        )

@router.post("/block", summary="Block another user")
async def block_user(
    request: BlockRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Block another user
    """
    try:
        # Check if user exists
        target_user = db.query(User).filter(User.id == request.blocked_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already blocked
        existing_block = db.query(UserBlock).filter(
            UserBlock.blocker_id == current_user.id,
            UserBlock.blocked_id == request.blocked_id
        ).first()
        
        if existing_block:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already blocking this user"
            )
        
        # Create new block
        block = UserBlock(
            blocker_id=current_user.id,
            blocked_id=request.blocked_id,
            reason=request.reason,
            is_permanent=request.is_permanent
        )
        
        db.add(block)
        db.commit()
        
        return {"message": "Successfully blocked user", "block_id": block.id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to block user: {str(e)}"
        )

@router.post("/mute", summary="Mute another user")
async def mute_user(
    request: MuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mute another user
    """
    try:
        # Check if user exists
        target_user = db.query(User).filter(User.id == request.muted_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already muted
        existing_mute = db.query(UserMute).filter(
            UserMute.muter_id == current_user.id,
            UserMute.muted_id == request.muted_id
        ).first()
        
        if existing_mute:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already muting this user"
            )
        
        # Create new mute
        mute = UserMute(
            muter_id=current_user.id,
            muted_id=request.muted_id,
            mute_stories=request.mute_stories,
            mute_posts=request.mute_posts,
            mute_comments=request.mute_comments,
            mute_messages=request.mute_messages
        )
        
        db.add(mute)
        db.commit()
        
        return {"message": "Successfully muted user", "mute_id": mute.id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mute user: {str(e)}"
        )

@router.get("/{user_id}/followers", summary="Get user's followers")
async def get_followers(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get list of users who follow the specified user
    """
    try:
        followers = db.query(UserRelationship).filter(
            UserRelationship.following_id == user_id,
            UserRelationship.relationship_type == RelationshipType.FOLLOWING
        ).all()
        
        return {
            "followers": [
                {
                    "follower_id": rel.follower_id,
                    "username": rel.follower.username,
                    "display_name": rel.follower.display_name,
                    "avatar_url": rel.follower.avatar_url,
                    "created_at": rel.created_at
                }
                for rel in followers
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get followers: {str(e)}"
        )

@router.get("/{user_id}/following", summary="Get users followed by user")
async def get_following(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get list of users followed by the specified user
    """
    try:
        following = db.query(UserRelationship).filter(
            UserRelationship.follower_id == user_id,
            UserRelationship.relationship_type == RelationshipType.FOLLOWING
        ).all()
        
        return {
            "following": [
                {
                    "following_id": rel.following_id,
                    "username": rel.following.username,
                    "display_name": rel.following.display_name,
                    "avatar_url": rel.following.avatar_url,
                    "created_at": rel.created_at
                }
                for rel in following
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get following: {str(e)}"
        )
