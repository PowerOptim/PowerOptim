"""
User model for authentication and user management
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.database import Base


class User(Base):
    """
    User table - stores user accounts and login credentials
    
    Each instance of this class = one row in the 'users' table
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Email - must be unique, used for login
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Password - stored as hash (e.g. $2b$12$KIXxkF8...)
    # never store plain text passwords!
    hashed_password = Column(String, nullable=False)
    
    # User's full name (optional)
    full_name = Column(String, nullable=True)
    
    # Is account active? (for soft deletes/banning users)
    is_active = Column(Boolean, default=True)
    
    # Timestamps - track when account was created/updated
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships - connect to other tables
    # This creates a "virtual" field that lets you access related data
    # user.sensor_readings will give you all EnergyReading rows for this user
    sensor_readings = relationship("SensorReading", back_populates="user")
    switch_events = relationship("SwitchEvent", back_populates="user")
    
    def __repr__(self):
        """
        String representation for debugging
        When you print(user), you'll see this
        """
        return f"<User(id={self.id}, email={self.email}, name={self.full_name})>"

"""
Creating a user:
----------------
from models.user import User
from database.database import get_db

def create_user(db: Session, email: str, password: str, name: str):
    # Hash the password first! (we'll add this function later)
    hashed_pw = hash_password(password)
    
    user = User(
        email=email,
        hashed_password=hashed_pw,
        full_name=name
    )
    
    db.add(user)        # Add to session
    db.commit()         # Save to database
    db.refresh(user)    # Get the auto-generated ID
    
    return user


Getting a user by email:
------------------------
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
    # Returns User object or None if not found


Getting a user by ID:
--------------------
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


Getting all users:
-----------------
def get_all_users(db: Session):
    return db.query(User).all()


Updating a user:
---------------
def update_user_name(db: Session, user_id: int, new_name: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.full_name = new_name
        db.commit()
    return user


Deleting a user (soft delete):
------------------------------
def deactivate_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
    return user
"""