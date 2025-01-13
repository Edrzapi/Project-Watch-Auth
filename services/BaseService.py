import logging
from fastapi import HTTPException, Depends
from sqlalchemy import MetaData
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional

from utils.ServerManager import ServerManager

T = TypeVar('T')

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def _raise_http_exception(status_code: int, detail: str, log_message: Optional[str] = None) -> None:
    """Helper function to raise an HTTPException with optional logging."""
    if log_message:
        logger.error(log_message)
    raise HTTPException(status_code=status_code, detail=detail)


class BaseService(Generic[T]):

    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session
        self.metadata = MetaData()

    def get(self, item_id: int) -> T:
        """Retrieve a single item by ID."""
        try:
            item = self.session.query(self.model).get(item_id)
            if not item:
                _raise_http_exception(
                    status_code=404,
                    detail=f"Item with ID {item_id} not found",
                    log_message=f"Item with ID {item_id} not found"
                )
            return item
        except Exception as e:
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error retrieving item with ID {item_id}: {e}"
            )

    def get_all(self) -> List[T]:
        """Retrieve all items."""
        try:
            return self.session.query(self.model).all()
        except Exception as e:
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error retrieving items: {e}"
            )

    def get_by_name(self, name: str) -> Optional[T]:
        """Retrieve a single user by name."""
        try:
            user = self.session.query(self.model).filter(self.model.name == name).first()
            if not user:
                _raise_http_exception(
                    status_code=404,
                    detail=f"User with name '{name}' not found",
                    log_message=f"User with name '{name}' not found"
                )
            return user
        except Exception as e:
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error retrieving user with name '{name}': {e}"
            )

    def create(self, item: T) -> T:
        """Create a new item."""
        try:
            self.session.add(item)
            self.session.commit()
            self.session.refresh(item)
            return item
        except Exception as e:
            self.session.rollback()
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error creating item: {e}"
            )

    def update(self, item_id: int, updated_item: T) -> T:
        """Update an existing item."""
        try:
            db_item = self.get(item_id)  # Will raise 404 if not found
            for key, value in vars(updated_item).items():
                if value is not None:
                    setattr(db_item, key, value)
            self.session.commit()
            self.session.refresh(db_item)
            return db_item
        except HTTPException:
            raise
        except Exception as e:
            self.session.rollback()
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error updating item with ID {item_id}: {e}"
            )

    def delete(self, item_id: int) -> dict:
        """Delete an item by ID."""
        try:
            item = self.get(item_id)  # Will raise 404 if not found
            self.session.delete(item)
            self.session.commit()
            return {"message": f"Item with ID {item_id} deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            self.session.rollback()
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error deleting item with ID {item_id}: {e}"
            )
