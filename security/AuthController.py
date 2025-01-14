from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from security.AuthService import AuthService
from services.UserService import UserService
from utils.LoggingConfig import LoggerManager
from utils.ServiceDependency import get_service_dependency, GenericDependencies
from schemas import UserSchema as schema, TokenSchema

# Initialize logger
logger = LoggerManager().get_logger()

router = APIRouter()

# Get the dependencies for AuthService and UserService
get_auth_service_dependency = get_service_dependency(AuthService)
get_user_service_dependency = get_service_dependency(UserService)

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/register", response_model=schema.User, status_code=201)
def register_user(
        user: schema.UserCreate,
        deps: GenericDependencies[UserService] = Depends(get_user_service_dependency)):
    """Register a new user."""
    try:
        logger.info(f"Attempting to register user: {user.username}")  # Changed to username
        return deps.get_service().create_user(user)
    except HTTPException as e:
        logger.error(f"User registration failed: {e.detail}")
        raise e


@router.post("/login")
def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        deps: GenericDependencies[AuthService] = Depends(get_auth_service_dependency)
):
    """Authenticate user and return a JWT token."""
    auth_service = deps.get_service()
    user = auth_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate JWT token
    access_token = auth_service.create_access_token(data={"sub": user.username})  # Changed to username
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schema.User)
def get_current_user(
        token: str = Depends(oauth2_scheme),
        deps: GenericDependencies[AuthService] = Depends(get_auth_service_dependency)
):
    """Retrieve the currently authenticated user."""
    auth_service = deps.get_service()
    user = auth_service.get_current_user(token)
    return user
