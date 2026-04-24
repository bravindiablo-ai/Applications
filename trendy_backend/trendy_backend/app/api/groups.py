from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Group, GroupMember, User
from app.auth.middleware import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/groups", tags=["Groups"])

# Pydantic models
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True
    category: Optional[str] = None

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None

class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    avatar_url: Optional[str]
    cover_image_url: Optional[str]
    creator_id: int
    created_at: datetime
    is_public: bool
    is_verified: bool
    privacy_level: int
    max_members: int
    category: Optional[str]
    member_count: int = 0
    
    class Config:
        from_attributes = True

class GroupMemberResponse(BaseModel):
    id: int
    user_id: int
    role: str
    joined_at: datetime
    is_muted: bool
    is_banned: bool
    
    class Config:
        from_attributes = True

# API Endpoints
@router.post("/", response_model=GroupResponse)
async def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Create a new group
    """
    try:
        # Create the group
        new_group = Group(
            name=group.name,
            description=group.description,
            creator_id=user_id,
            is_public=group.is_public,
            category=group.category
        )
        
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        
        # Add the creator as a member with owner role
        group_member = GroupMember(
            group_id=new_group.id,
            user_id=user_id,
            role="owner"
        )
        
        db.add(group_member)
        db.commit()
        
        # Get member count
        member_count = db.query(GroupMember).filter(GroupMember.group_id == new_group.id).count()
        
        return GroupResponse(
            id=new_group.id,
            name=new_group.name,
            description=new_group.description,
            avatar_url=new_group.avatar_url,
            cover_image_url=new_group.cover_image_url,
            creator_id=new_group.creator_id,
            created_at=new_group.created_at,
            is_public=new_group.is_public,
            is_verified=new_group.is_verified,
            privacy_level=new_group.privacy_level,
            max_members=new_group.max_members,
            category=new_group.category,
            member_count=member_count
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create group: {str(e)}")

@router.get("/", response_model=List[GroupResponse])
async def get_groups(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Get groups the user is a member of or public groups
    """
    try:
        # Get groups the user is a member of
        user_groups = db.query(Group).join(GroupMember).filter(
            GroupMember.user_id == user_id
        )
        
        # Get public groups
        public_groups = db.query(Group).filter(Group.is_public == True)
        
        # Combine and deduplicate
        all_groups = user_groups.union(public_groups).order_by(Group.created_at.desc()).offset(skip).limit(limit).all()
        
        # Add member counts
        groups_with_counts = []
        for group in all_groups:
            member_count = db.query(GroupMember).filter(GroupMember.group_id == group.id).count()
            groups_with_counts.append(GroupResponse(
                id=group.id,
                name=group.name,
                description=group.description,
                avatar_url=group.avatar_url,
                cover_image_url=group.cover_image_url,
                creator_id=group.creator_id,
                created_at=group.created_at,
                is_public=group.is_public,
                is_verified=group.is_verified,
                privacy_level=group.privacy_level,
                max_members=group.max_members,
                category=group.category,
                member_count=member_count
            ))
        
        return groups_with_counts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve groups: {str(e)}")

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Get a specific group
    """
    try:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user has access to this group
        if not group.is_public:
            group_member = db.query(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            ).first()
            
            if not group_member:
                raise HTTPException(status_code=403, detail="You are not a member of this group")
        
        # Get member count
        member_count = db.query(GroupMember).filter(GroupMember.group_id == group_id).count()
        
        return GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            avatar_url=group.avatar_url,
            cover_image_url=group.cover_image_url,
            creator_id=group.creator_id,
            created_at=group.created_at,
            is_public=group.is_public,
            is_verified=group.is_verified,
            privacy_level=group.privacy_level,
            max_members=group.max_members,
            category=group.category,
            member_count=member_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve group: {str(e)}")

@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_update: GroupUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Update a group (only allowed for owners)
    """
    try:
        # Get the group
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user is the owner
        group_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
            GroupMember.role == "owner"
        ).first()
        
        if not group_member:
            raise HTTPException(status_code=403, detail="You are not the owner of this group")
        
        # Update the group
        if group_update.name is not None:
            group.name = group_update.name
        if group_update.description is not None:
            group.description = group_update.description
        if group_update.is_public is not None:
            group.is_public = group_update.is_public
        if group_update.category is not None:
            group.category = group_update.category
        
        db.commit()
        db.refresh(group)
        
        # Get member count
        member_count = db.query(GroupMember).filter(GroupMember.group_id == group.id).count()
        
        return GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            avatar_url=group.avatar_url,
            cover_image_url=group.cover_image_url,
            creator_id=group.creator_id,
            created_at=group.created_at,
            is_public=group.is_public,
            is_verified=group.is_verified,
            privacy_level=group.privacy_level,
            max_members=group.max_members,
            category=group.category,
            member_count=member_count
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update group: {str(e)}")

@router.delete("/{group_id}")
async def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Delete a group (only allowed for owners)
    """
    try:
        # Get the group
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user is the owner
        group_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
            GroupMember.role == "owner"
        ).first()
        
        if not group_member:
            raise HTTPException(status_code=403, detail="You are not the owner of this group")
        
        # Delete all group members
        db.query(GroupMember).filter(GroupMember.group_id == group_id).delete()
        
        # Delete the group
        db.delete(group)
        db.commit()
        
        return {"message": "Group deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete group: {str(e)}")

@router.post("/{group_id}/members", response_model=GroupMemberResponse)
async def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Join a group
    """
    try:
        # Check if group exists
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user is already a member
        existing_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ).first()
        
        if existing_member:
            raise HTTPException(status_code=400, detail="You are already a member of this group")
        
        # Create group member
        group_member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            role="member"
        )
        
        db.add(group_member)
        db.commit()
        db.refresh(group_member)
        
        return group_member
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to join group: {str(e)}")

@router.delete("/{group_id}/members")
async def leave_group(
    group_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Leave a group
    """
    try:
        # Check if group exists
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user is a member
        group_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ).first()
        
        if not group_member:
            raise HTTPException(status_code=400, detail="You are not a member of this group")
        
        # Check if user is the owner
        if group_member.role == "owner":
            raise HTTPException(status_code=400, detail="Owners cannot leave their own group. Delete the group instead.")
        
        # Remove group member
        db.delete(group_member)
        db.commit()
        
        return {"message": "Left group successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to leave group: {str(e)}")

@router.get("/{group_id}/members", response_model=List[GroupMemberResponse])
async def get_group_members(
    group_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Get members of a group
    """
    try:
        # Check if group exists
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user has access to this group
        if not group.is_public:
            group_member = db.query(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            ).first()
            
            if not group_member:
                raise HTTPException(status_code=403, detail="You are not a member of this group")
        
        # Get group members
        members = db.query(GroupMember).filter(
            GroupMember.group_id == group_id
        ).order_by(GroupMember.joined_at.desc()).offset(skip).limit(limit).all()
        
        return members
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve group members: {str(e)}")