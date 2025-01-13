from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from schemas import UserSchema as schema
from services.UserService import UserService
from security.AuthService import AuthService
from utils.ServiceDependency import get_service_dependency, GenericDependencies

router = APIRouter()
user_service_dependency = get_service_dependency(UserService)
auth_service_dependency = get_service_dependency(AuthService)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Endpoint to create a new user
@router.post("/create", response_model=schema.User, status_code=status.HTTP_201_CREATED)
def create_user(
        user: schema.UserCreate,
        user_deps: GenericDependencies[UserService] = Depends(user_service_dependency)
):
    """Create a new user, ensuring no duplicates."""
    try:
        return user_deps.get_service().create_user(user)
    except HTTPException as e:
        raise e


# Endpoint to read a user by ID
@router.get("/read/{user_id}", response_model=schema.User, status_code=status.HTTP_200_OK)
def read_user(
        user_id: int,
        user_deps: GenericDependencies[UserService] = Depends(user_service_dependency)
):
    """Read a user by ID."""
    try:
        return user_deps.get_service().get_user(user_id)
    except HTTPException as e:
        raise e


# Endpoint to read all users
@router.get("/read", response_model=List[schema.User], status_code=status.HTTP_200_OK)
def read_users(user_deps: GenericDependencies[UserService] = Depends(user_service_dependency)):
    """Read all users."""
    try:
        return user_deps.get_service().get_all_users()
    except HTTPException as e:
        raise e


# Endpoint to retrieve a user by name
@router.get("/user/read/{name}", response_model=schema.User, status_code=status.HTTP_200_OK)
def get_user_by_name(
        name: str,
        user_deps: GenericDependencies[UserService] = Depends(user_service_dependency)
):
    """Retrieve a user by name."""
    try:
        user = user_deps.get_service().get_by_name(name)
        return user
    except HTTPException as e:
        raise e


# Endpoint to update an existing user
@router.put("/update/{user_id}", response_model=schema.User, status_code=status.HTTP_200_OK)
def update_user(
        user_id: int,
        user: schema.UserUpdate,
        user_deps: GenericDependencies[UserService] = Depends(user_service_dependency)
):
    """Update an existing user."""
    try:
        return user_deps.get_service().update_user(user_id, user)
    except HTTPException as e:
        raise e


# Endpoint to delete a user by ID
@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: int,
        user_deps: GenericDependencies[UserService] = Depends(user_service_dependency)
):
    """Delete a user by ID."""
    try:
        user_deps.get_service().delete_user(user_id)
        return
    except HTTPException as e:
        raise e
