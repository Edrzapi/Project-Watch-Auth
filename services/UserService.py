from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models.SQLModel import User, UserProfile
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

        # Create the user profile, using empty strings if first_name or last_name are None
        profile = UserProfile(
            first_name=user_data.first_name or '',  # Use empty string if None
            last_name=user_data.last_name or '',  # Use empty string if None
        )

        # Create the user with the profile
        new_user = User(
            username=user_data.username,
            password_hash=hashed_password,  # Use the hashed password
            profile=profile,  # Create the associated user profile
        )

        return self.create(new_user)

    def get_user(self, user_id: int) -> schema.UserFullResponse:
        """Retrieve a single user by ID, including profile details."""
        # Fetch the user by ID, and check if it exists
        existing_user = self.get(user_id)
        if not existing_user:
            raise ValueError("User not found")

        # Map the User and UserProfile to the UserFullResponse schema
        user_profile = existing_user.profile if existing_user.profile else None

        # Prepare the full response model
        user_response = schema.UserFullResponse(
            user_id=existing_user.user_id,
            username=existing_user.username,
            password_hash=existing_user.password_hash,
            is_active=existing_user.is_active,
            created_at=existing_user.created_at,
            updated_at=existing_user.updated_at,
            profile=user_profile,
        )
        return user_response

    def get_all_users(self) -> list[schema.UserFullResponse]:
        """Retrieve all users."""
        all_users = self.get_all()
        return [
            schema.UserFullResponse(
                user_id=user.user_id,
                username=user.username,
                password_hash=user.password_hash,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                profile=user.profile,  # This will include the profile details if available
            )
            for user in all_users
        ]

    def update_user(self, user_id: int, user_data: schema.UserUpdate) -> User:
        """Update an existing user."""
        # Fetch the user by ID
        existing_user = self.session.query(User).filter(User.user_id == user_id).first()

        if not existing_user:
            raise ValueError("User not found")

        # Update the username if provided
        if user_data.username:
            existing_user.username = user_data.username

        # Update the password if provided
        if user_data.password:
            existing_user.password_hash = self.pwd_context.hash(user_data.password)

        # Update the is_active flag if provided
        if user_data.is_active is not None:
            existing_user.is_active = user_data.is_active

        # Update the profile fields (first_name, last_name) if provided
        if user_data.first_name or user_data.last_name:
            if not existing_user.profile:
                # If no profile exists, create a new one
                existing_user.profile = UserProfile()

            if user_data.first_name:
                existing_user.profile.first_name = user_data.first_name
            if user_data.last_name:
                existing_user.profile.last_name = user_data.last_name

        # Commit the changes to the database
        self.session.commit()

        # Refresh the user object to reflect the updated values
        self.session.refresh(existing_user)

        return existing_user

    def delete_user(self, user_id: int) -> dict:
        """Delete a user by ID."""
        # Fetch the user with the associated profile (cascade delete will handle the profile)
        user = self.session.query(User).filter(User.user_id == user_id).first()

        if not user:
            raise ValueError("User not found")

        # Delete the user and commit the changes (profile will be deleted automatically)
        self.session.delete(user)
        self.session.commit()

        return {"message": "User deleted successfully"}

    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a single user by username."""
        return self.session.query(User).filter(User.username == username).first()
