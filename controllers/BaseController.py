import logging
from fastapi import HTTPException, Depends
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


class BaseController(Generic[T]):

    def __init__(self, model: Type[T], db_session: Session = Depends(ServerManager)):
        self.model = model
        self.db_session = db_session

    def get(self, item_id: int) -> T:
        """Retrieve a single item by ID."""
        try:
            item = self.db_session.query(self.model).get(item_id)
            if not item:
                _raise_http_exception(
                    status_code=404,
                    detail=f"{self.model.__name__} with ID {item_id} not found",
                    log_message=f"{self.model.__name__} with ID {item_id} not found"
                )
            return item
        except HTTPException:
            raise  # Reraise HTTP exceptions for uniform handling
        except Exception as e:
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error retrieving {self.model.__name__} with ID {item_id}: {e}"
            )

    def get_all(self) -> List[T]:
        """Retrieve all items."""
        try:
            return self.db_session.query(self.model).all()
        except Exception as e:
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error retrieving all {self.model.__name__}: {e}"
            )

    def create(self, item: T) -> T:
        """Create a new item."""
        try:
            self.db_session.add(item)
            self.db_session.commit()
            self.db_session.refresh(item)
            return item
        except Exception as e:
            self.db_session.rollback()
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error creating {self.model.__name__}: {e}"
            )

    def update(self, item_id: int, updated_item: T) -> T:
        """Update an existing item."""
        try:
            db_item = self.get(item_id)  # Will raise 404 if not found
            for key, value in vars(updated_item).items():
                if value is not None:
                    setattr(db_item, key, value)
            self.db_session.commit()
            self.db_session.refresh(db_item)
            return db_item
        except HTTPException:
            raise  # Reraise HTTP exceptions for uniform handling
        except Exception as e:
            self.db_session.rollback()
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error updating {self.model.__name__} with ID {item_id}: {e}"
            )

    def delete(self, item_id: int) -> dict:
        """Delete an item by ID."""
        try:
            item = self.get(item_id)  # Will raise 404 if not found
            self.db_session.delete(item)
            self.db_session.commit()
            return {"message": f"{self.model.__name__} with ID {item_id} deleted successfully"}
        except HTTPException:
            raise  # Reraise HTTP exceptions for uniform handling
        except Exception as e:
            self.db_session.rollback()
            _raise_http_exception(
                status_code=500,
                detail="Internal server error",
                log_message=f"Error deleting {self.model.__name__} with ID {item_id}: {e}"
            )
