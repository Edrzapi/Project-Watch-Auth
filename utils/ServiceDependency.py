from fastapi import Depends
from typing import Type, TypeVar, Generic
from utils.ServerManager import ServerManager
from sqlalchemy.orm import Session

T = TypeVar('T')


class GenericDependencies(Generic[T]):
    def __init__(self, service_class: Type[T], db_manager: ServerManager, session: Session):
        self.db_manager = db_manager
        self.service = service_class(session)  # Pass the session directly to the service

    def get_service(self) -> T:
        return self.service


# Factory function to create the dependency with the specific service class
def get_service_dependency(service_class: Type[T]):
    def _get_dependency(db_manager: ServerManager = Depends(lambda: ServerManager())) -> GenericDependencies[T]:
        session = db_manager.get_session()  # Get the session from the ServerManager
        try:
            deps = GenericDependencies(service_class, db_manager, session)
            yield deps
        finally:
            session.close()  # Ensure the session is closed after the request

    return _get_dependency


