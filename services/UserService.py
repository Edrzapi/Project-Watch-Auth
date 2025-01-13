from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.SQLModel import User
from schemas import UserSchema as schema  # Assuming you have a UserSchema defined
from services.BaseService import BaseService  # Import your BaseService


class UserService(BaseService[User]):
    def __init__(self, session: Session):
        super().__init__(model=User, session=session)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Initialize password context

    def create_user(self, user_data: schema.UserCreate) -> User:
        """Create a new user."""
        # Hash the password before creating the user
        hashed_password = self.pwd_context.hash(user_data.password)

        new_user = User(
            email=user_data.email,
            name=user_data.name,
            password=hashed_password,  # Use the hashed password
            phone=user_data.phone,
        )
        return self.create(new_user)

    def get_user(self, user_id: int) -> User:
        """Retrieve a single user by ID."""
        return self.get(user_id)

    def get_all_users(self) -> list[User]:
        """Retrieve all users."""
        return self.get_all()

    def update_user(self, user_id: int, user_data: schema.UserUpdate) -> User:
        """Update an existing user."""
        # Hash the new password if it's being updated
        hashed_password = self.pwd_context.hash(user_data.password) if user_data.password else None

        updated_user = User(
            email=user_data.email,
            name=user_data.name,
            password=hashed_password,  # Use the hashed password
            phone=user_data.phone,
        )
        return self.update(user_id, updated_user)

    def delete_user(self, user_id: int) -> dict:
        """Delete a user by ID."""
        return self.delete(user_id)

    def get_by_name(self, name: str) -> User:
        """Retrieve a single user by name."""
        return self.get_user_by_name(name)
