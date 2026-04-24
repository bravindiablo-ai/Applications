from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from app.database import get_db
from app.models import Message, Group, GroupMember, User
from app.auth.middleware import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/messages", tags=["Messages"])

# Pydantic models
class MessageCreate(BaseModel):
    receiver_id: Optional[int] = None
    group_id: Optional[int] = None
    content: str
    media_url: Optional[str] = None
    message_type: str = "text"  # text, image, video, audio, file
    reply_to_message_id: Optional[int] = None

class MessageUpdate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: Optional[int]
    group_id: Optional[int]
    content: str
    media_url: Optional[str]
    message_type: str
    sent_at: datetime
    read_at: Optional[datetime]
    is_deleted: bool
    is_burn_after_reading: bool
    expires_at: Optional[datetime]
    reply_to_message_id: Optional[int]
    is_edited: bool
    edited_at: Optional[datetime]
    
    class Config:
        orm_mode = True

class ThreadedMessageResponse(MessageResponse):
    replies: List[MessageResponse] = []

class VoiceChannelCreate(BaseModel):
    group_id: int
    name: str
    description: Optional[str] = None
    max_participants: int = 100

class VoiceChannelResponse(BaseModel):
    id: int
    group_id: int
    name: str
    description: Optional[str]
    created_at: datetime
    is_active: bool
    participants: List[int] = []
    
    class Config:
        orm_mode = True

# In-memory storage for active voice channels (in production, use Redis or similar)
active_voice_channels: Dict[int, Dict[str, Any]] = {}

# API Endpoints
@router.post("/", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Create a new message (direct message or group message)
    """
    try:
        # Validate that either receiver_id or group_id is provided
        if not message.receiver_id and not message.group_id:
            raise HTTPException(status_code=400, detail="Either receiver_id or group_id must be provided")
        
        # If it's a group message, verify user is a member of the group
        if message.group_id:
            group_member = db.query(GroupMember).filter(
                GroupMember.group_id == message.group_id,
                GroupMember.user_id == user_id
            ).first()
            
            if not group_member:
                raise HTTPException(status_code=403, detail="You are not a member of this group")
        
        # If it's a direct message, verify receiver exists
        if message.receiver_id:
            receiver = db.query(User).filter(User.id == message.receiver_id).first()
            if not receiver:
                raise HTTPException(status_code=404, detail="Receiver not found")
        
        # If it's a reply, verify the parent message exists
        if message.reply_to_message_id:
            parent_message = db.query(Message).filter(Message.id == message.reply_to_message_id).first()
            if not parent_message:
                raise HTTPException(status_code=404, detail="Parent message not found")
        
        # Create the message
        new_message = Message(
            sender_id=user_id,
            receiver_id=message.receiver_id,
            group_id=message.group_id,
            content=message.content,
            media_url=message.media_url,
            message_type=message.message_type,
            reply_to_message_id=message.reply_to_message_id
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        return new_message
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")

@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Get messages for the current user (both sent and received)
    """
    try:
        messages = db.query(Message).filter(
            (Message.sender_id == user_id) | 
            (Message.receiver_id == user_id) |
            (Message.group_id.in_(
                db.query(GroupMember.group_id).filter(GroupMember.user_id == user_id)
            ))
        ).order_by(Message.sent_at.desc()).offset(skip).limit(limit).all()
        
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages: {str(e)}")

@router.get("/thread/{message_id}", response_model=ThreadedMessageResponse)
async def get_message_thread(
    message_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Get a message and all its replies (threaded view)
    """
    try:
        # Get the parent message
        parent_message = db.query(Message).filter(Message.id == message_id).first()
        if not parent_message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Check if user has access to this message
        if parent_message.group_id:
            # Group message - check if user is member
            group_member = db.query(GroupMember).filter(
                GroupMember.group_id == parent_message.group_id,
                GroupMember.user_id == user_id
            ).first()
            
            if not group_member:
                raise HTTPException(status_code=403, detail="You are not a member of this group")
        elif parent_message.receiver_id != user_id and parent_message.sender_id != user_id:
            # Direct message - check if user is sender or receiver
            raise HTTPException(status_code=403, detail="You do not have access to this message")
        
        # Get all replies to this message
        replies = db.query(Message).filter(
            Message.reply_to_message_id == message_id
        ).order_by(Message.sent_at.asc()).all()
        
        # Create response with replies
        response = ThreadedMessageResponse(
            id=parent_message.id,
            sender_id=parent_message.sender_id,
            receiver_id=parent_message.receiver_id,
            group_id=parent_message.group_id,
            content=parent_message.content,
            media_url=parent_message.media_url,
            message_type=parent_message.message_type,
            sent_at=parent_message.sent_at,
            read_at=parent_message.read_at,
            is_deleted=parent_message.is_deleted,
            is_burn_after_reading=parent_message.is_burn_after_reading,
            expires_at=parent_message.expires_at,
            reply_to_message_id=parent_message.reply_to_message_id,
            is_edited=parent_message.is_edited,
            edited_at=parent_message.edited_at,
            replies=[MessageResponse.model_validate(reply) for reply in replies]
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve message thread: {str(e)}")

@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    message_update: MessageUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Update a message (only allowed for the sender)
    """
    try:
        # Get the message
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Check if user is the sender
        if message.sender_id != user_id:
            raise HTTPException(status_code=403, detail="You can only edit your own messages")
        
        # Update the message
        message.content = message_update.content
        message.is_edited = True
        message.edited_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        
        return message
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update message: {str(e)}")

@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Delete a message (only allowed for the sender)
    """
    try:
        # Get the message
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Check if user is the sender
        if message.sender_id != user_id:
            raise HTTPException(status_code=403, detail="You can only delete your own messages")
        
        # Mark as deleted (soft delete)
        message.is_deleted = True
        
        db.commit()
        
        return {"message": "Message deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")

# Voice Channel Endpoints
@router.post("/voice-channels", response_model=VoiceChannelResponse)
async def create_voice_channel(
    voice_channel: VoiceChannelCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Create a new voice channel in a group
    """
    try:
        # Verify user is a member of the group and has permission to create voice channels
        group_member = db.query(GroupMember).filter(
            GroupMember.group_id == voice_channel.group_id,
            GroupMember.user_id == user_id
        ).first()
        
        if not group_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")
        
        # In a real implementation, you would check if the user has permission to create voice channels
        # For now, we'll allow any group member to create voice channels
        
        # Create the voice channel in memory (in production, store in database)
        channel_id = len(active_voice_channels) + 1
        active_voice_channels[channel_id] = {
            "id": channel_id,
            "group_id": voice_channel.group_id,
            "name": voice_channel.name,
            "description": voice_channel.description,
            "created_at": datetime.utcnow(),
            "is_active": True,
            "participants": []
        }
        
        return VoiceChannelResponse(
            id=channel_id,
            group_id=voice_channel.group_id,
            name=voice_channel.name,
            description=voice_channel.description,
            created_at=active_voice_channels[channel_id]["created_at"],
            is_active=True,
            participants=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create voice channel: {str(e)}")

@router.post("/voice-channels/{channel_id}/join")
async def join_voice_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Join a voice channel
    """
    try:
        # Check if channel exists
        if channel_id not in active_voice_channels:
            raise HTTPException(status_code=404, detail="Voice channel not found")
        
        # Verify user is a member of the group
        group_id = active_voice_channels[channel_id]["group_id"]
        group_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ).first()
        
        if not group_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")
        
        # Add user to channel participants
        if user_id not in active_voice_channels[channel_id]["participants"]:
            active_voice_channels[channel_id]["participants"].append(user_id)
        
        return {"message": "Joined voice channel successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join voice channel: {str(e)}")

@router.post("/voice-channels/{channel_id}/leave")
async def leave_voice_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Leave a voice channel
    """
    try:
        # Check if channel exists
        if channel_id not in active_voice_channels:
            raise HTTPException(status_code=404, detail="Voice channel not found")
        
        # Remove user from channel participants
        if user_id in active_voice_channels[channel_id]["participants"]:
            active_voice_channels[channel_id]["participants"].remove(user_id)
        
        return {"message": "Left voice channel successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to leave voice channel: {str(e)}")

@router.get("/voice-channels/{group_id}", response_model=List[VoiceChannelResponse])
async def get_group_voice_channels(
    group_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Get all voice channels for a group
    """
    try:
        # Verify user is a member of the group
        group_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ).first()
        
        if not group_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")
        
        # Get all voice channels for this group
        group_channels = [
            VoiceChannelResponse(
                id=channel_id,
                group_id=channel["group_id"],
                name=channel["name"],
                description=channel["description"],
                created_at=channel["created_at"],
                is_active=channel["is_active"],
                participants=channel["participants"]
            )
            for channel_id, channel in active_voice_channels.items()
            if channel["group_id"] == group_id
        ]
        
        return group_channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve voice channels: {str(e)}")

# WebSocket endpoint for real-time messaging
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time messaging
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process the message and broadcast to relevant users
            # This is a simplified implementation - in production, you would use
            # a proper message broker like Redis Pub/Sub
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass