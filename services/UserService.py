import logging
from fastapi import HTTPException, Depends
from typing import Optional, List
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError

from models.SQLModel import User, UserProfile
from schemas import UserSchema as schema  # Assuming you have a UserSchema defined
from services.BaseService import BaseService  # Import your BaseService


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

def _raise_http_exception(status_code: int, detail: str, log_message: Optional[str] = None) -> None:
    """Helper function to raise an HTTPException with optional logging."""
    if log_message:
        logger.error(log_message)
    raise HTTPException(status_code=status_code, detail=detail)

class UserService(BaseService[User]):
    def __init__(self, session: Session):
        super().__init__(model=User, session=session)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Initialize password context

    def create_user(self, user_data: schema.UserCreate) -> User:
        """Create a new user."""
        try:
            # Check if the username already exists
            existing_user = self.session.query(User).filter(User.username == user_data.username).first()
            if existing_user:
                _raise_http_exception(
                    status_code=400,
                    detail="Username already exists",
                    log_message=f"Attempted to create user with existing username: {user_data.username}"
                )

            # Hash the password before saving the user
            hashed_password = self.pwd_context.hash(user_data.password)

            # Create the user profile
            profile = UserProfile(
                first_name=user_data.first_name or '',
                last_name=user_data.last_name or '',
            )

            # Create the new user
            new_user = User(
                username=user_data.username,
                password_hash=hashed_password,
                profile=profile,
            )

            return self.create(new_user)  # Reuses the `create` method from BaseService

        except Exception as e:
            self.session.rollback()

            # Check the exception message and handle based on that
            if "Username already exists" in str(e):
                # Specific case for username conflict
                _raise_http_exception(
                    status_code=409,
                    detail="Username already exists",
                    log_message=f"Error creating user: {e}"
                )
            elif "IntegrityError" in str(e):
                # Handle IntegrityError
                _raise_http_exception(
                    status_code=400,
                    detail="IntegrityError, please check details and try again.",
                    log_message=f"IntegrityError: {e.orig}"
                )
            elif "OperationalError" in str(e):
                # Handle OperationalError (e.g., DB connection issues)
                _raise_http_exception(
                    status_code=500,
                    detail="Database operation error while creating user",
                    log_message=f"OperationalError: {e.orig}"
                )
            elif "DataError" in str(e):
                # Handle DataError (e.g., invalid data)
                _raise_http_exception(
                    status_code=400,
                    detail="Invalid data error while creating user",
                    log_message=f"DataError: {e.orig}"
                )
            elif "ProgrammingError" in str(e):
                # Handle SQL programming error
                _raise_http_exception(
                    status_code=500,
                    detail="SQL programming error while creating user",
                    log_message=f"ProgrammingError: {e.orig}"
                )
            else:
                # Generic case for other exceptions
                _raise_http_exception(
                    status_code=500,
                    detail="Internal server error while creating user",
                    log_message=f"Error creating user: {e}"
                )

    def get_user(self, user_id: int) -> schema.UserFullResponse:
        """Retrieve a single user by ID, including profile details."""
        try:
            existing_user = self.get(user_id)  # Reuses the `get` method from BaseService
            user_profile = existing_user.profile if existing_user.profile else None

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
        except Exception as e:
            _raise_http_exception(
                status_code=404,
                detail=f"User with ID {user_id} not found",
                log_message=f"Error retrieving user with ID {user_id}: {e}"
            )

    def get_all_users(self) -> List[schema.UserFullResponse]:
        """Retrieve all users."""
        try:
            all_users = self.get_all()  # Reuses the `get_all` method from BaseService
            return [
                schema.UserFullResponse(
                    user_id=user.user_id,
                    username=user.username,
                    password_hash=user.password_hash,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    profile=user.profile,
                )
                for user in all_users
            ]
        except Exception as e:
            _raise_http_exception(
                status_code=500,
                detail="Internal server error while fetching users",
                log_message=f"Error retrieving all users: {e}"
            )

    def update_user(self, user_id: int, user_data: schema.UserUpdate) -> User:
        """Update an existing user."""
        try:
            existing_user = self.get(user_id)  # Reuses the `get` method from BaseService

            if user_data.username:
                existing_user.username = user_data.username

            if user_data.password:
                existing_user.password_hash = self.pwd_context.hash(user_data.password)

            if user_data.is_active is not None:
                existing_user.is_active = user_data.is_active

            if user_data.first_name or user_data.last_name:
                if not existing_user.profile:
                    existing_user.profile = UserProfile()

                if user_data.first_name:
                    existing_user.profile.first_name = user_data.first_name
                if user_data.last_name:
                    existing_user.profile.last_name = user_data.last_name

            self.session.commit()
            self.session.refresh(existing_user)

            return existing_user
        except Exception as e:
            _raise_http_exception(
                status_code=404,
                detail=f"User with ID {user_id} not found for update",
                log_message=f"Error updating user with ID {user_id}: {e}"
            )

    def delete_user(self, user_id: int) -> dict:
        """Delete a user by ID."""
        try:
            return self.delete(user_id)  # Reuses the `delete` method from BaseService
        except Exception as e:
            _raise_http_exception(
                status_code=404,
                detail=f"User with ID {user_id} not found for deletion",
                log_message=f"Error deleting user with ID {user_id}: {e}"
            )

    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by username."""
        try:
            user = self.session.query(User).filter(User.username == username).first()
            if not user:
                _raise_http_exception(
                    status_code=404,
                    detail=f"User with username '{username}' not found",
                    log_message=f"Error retrieving user with username '{username}': Not found"
                )
            return user
        except Exception as e:
            _raise_http_exception(
                status_code=500,
                detail="Internal server error while fetching user by username",
                log_message=f"Error retrieving user by username '{username}': {e}"
            )

