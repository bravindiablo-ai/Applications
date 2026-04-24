from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.follow import Follow, RelationshipType

def follow_user(db: Session, follower_id: int, followee_id: int):
    """Follow a user. If mutual follow, upgrade to friend."""
    if follower_id == followee_id:
        return {"error": "cannot follow self"}

    # Check if relationship already exists
    existing = db.query(Follow).filter(
        and_(Follow.follower_id == follower_id, Follow.followee_id == followee_id)
    ).first()

    if existing:
        if existing.relationship_type == RelationshipType.block:
            return {"error": "cannot follow blocked user"}
        return {"status": "already_following"}

    # Check if the other user is following back (for friend relationship)
    reverse_follow = db.query(Follow).filter(
        and_(Follow.follower_id == followee_id, Follow.followee_id == follower_id)
    ).first()

    relationship_type = RelationshipType.friend if reverse_follow else RelationshipType.follow

    f = Follow(
        follower_id=follower_id,
        followee_id=followee_id,
        relationship_type=relationship_type
    )
    db.add(f)

    # If this creates a mutual follow, update the reverse relationship to friend
    if reverse_follow and reverse_follow.relationship_type == RelationshipType.follow:
        reverse_follow.relationship_type = RelationshipType.friend

    db.commit()
    return {"status": "followed", "relationship_type": relationship_type.value}

def unfollow_user(db: Session, follower_id: int, followee_id: int):
    """Unfollow a user. If was friend, downgrade reverse to follow."""
    follow = db.query(Follow).filter(
        and_(Follow.follower_id == follower_id, Follow.followee_id == followee_id)
    ).first()

    if not follow:
        return {"status": "not_following"}

    # Check if this was a mutual friendship
    reverse_follow = db.query(Follow).filter(
        and_(Follow.follower_id == followee_id, Follow.followee_id == follower_id)
    ).first()

    db.delete(follow)

    # If there was a mutual friendship, downgrade the reverse to follow
    if reverse_follow and reverse_follow.relationship_type == RelationshipType.friend:
        reverse_follow.relationship_type = RelationshipType.follow

    db.commit()
    return {"status": "unfollowed"}

def block_user(db: Session, blocker_id: int, blocked_id: int):
    """Block a user. This removes any existing follow relationships."""
    if blocker_id == blocked_id:
        return {"error": "cannot block self"}

    # Remove any existing follow relationships between these users
    existing_follows = db.query(Follow).filter(
        or_(
            and_(Follow.follower_id == blocker_id, Follow.followee_id == blocked_id),
            and_(Follow.follower_id == blocked_id, Follow.followee_id == blocker_id)
        )
    ).all()

    for follow in existing_follows:
        db.delete(follow)

    # Create block relationship
    block = Follow(
        follower_id=blocker_id,
        followee_id=blocked_id,
        relationship_type=RelationshipType.block
    )
    db.add(block)
    db.commit()
    return {"status": "blocked"}

def unblock_user(db: Session, blocker_id: int, blocked_id: int):
    """Unblock a user."""
    block = db.query(Follow).filter(
        and_(
            Follow.follower_id == blocker_id,
            Follow.followee_id == blocked_id,
            Follow.relationship_type == RelationshipType.block
        )
    ).first()

    if not block:
        return {"status": "not_blocked"}

    db.delete(block)
    db.commit()
    return {"status": "unblocked"}

def get_relationship_status(db: Session, user_id: int, other_user_id: int):
    """Get the relationship status between two users."""
    relationship = db.query(Follow).filter(
        or_(
            and_(Follow.follower_id == user_id, Follow.followee_id == other_user_id),
            and_(Follow.follower_id == other_user_id, Follow.followee_id == user_id)
        )
    ).first()

    if not relationship:
        return {"status": "none"}

    if relationship.follower_id == user_id:
        return {
            "status": relationship.relationship_type.value,
            "direction": "outgoing" if relationship.relationship_type != RelationshipType.block else "blocking"
        }
    else:
        return {
            "status": relationship.relationship_type.value,
            "direction": "incoming"
        }

def get_followers(db: Session, user_id: int, limit: int = 50):
    """Get users following this user (excluding blocks)."""
    rows = db.query(Follow).filter(
        and_(
            Follow.followee_id == user_id,
            Follow.relationship_type.in_([RelationshipType.follow, RelationshipType.friend])
        )
    ).limit(limit).all()
    return [{"follower_id": r.follower_id, "since": r.created_at.isoformat(), "relationship_type": r.relationship_type.value} for r in rows]

def get_following(db: Session, user_id: int, limit: int = 50):
    """Get users this user is following (excluding blocks)."""
    rows = db.query(Follow).filter(
        and_(
            Follow.follower_id == user_id,
            Follow.relationship_type.in_([RelationshipType.follow, RelationshipType.friend])
        )
    ).limit(limit).all()
    return [{"followee_id": r.followee_id, "since": r.created_at.isoformat(), "relationship_type": r.relationship_type.value} for r in rows]

def get_friends(db: Session, user_id: int, limit: int = 50):
    """Get mutual friends."""
    rows = db.query(Follow).filter(
        and_(
            Follow.follower_id == user_id,
            Follow.relationship_type == RelationshipType.friend
        )
    ).limit(limit).all()
    return [{"friend_id": r.followee_id, "since": r.created_at.isoformat()} for r in rows]

def get_blocked_users(db: Session, user_id: int, limit: int = 50):
    """Get users blocked by this user."""
    rows = db.query(Follow).filter(
        and_(
            Follow.follower_id == user_id,
            Follow.relationship_type == RelationshipType.block
        )
    ).limit(limit).all()
    return [{"blocked_id": r.followee_id, "since": r.created_at.isoformat()} for r in rows]
