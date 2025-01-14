from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', nullable=True)
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', nullable=True)

    # Relationship with UserProfile
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete")

    def __repr__(self):
        return f"<User(username={self.username}, is_active={self.is_active})>"


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)

    # Relationship with User
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(first_name={self.first_name}, last_name={self.last_name})>"
