from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError

from utils.LoggingConfig import LoggerManager

# Initialize logger
logger = LoggerManager().get_logger()


class DatabaseConfig:

    def __init__(self, secret: dict):
        self.secret = secret

    def get_db_url(self, schema_name=None) -> str:
        """Returns the database URL for creating an engine."""
        db_url = f"mysql+pymysql://{self.secret['username']}:{self.secret['password']}@{self.secret['host']}:{self.secret.get('port', 3306)}/"
        if schema_name:
            db_url += schema_name
        return db_url

    def schema_exists(self, schema_name: str) -> bool:
        """Checks if the specified schema exists in the database."""
        try:
            engine = create_engine(self.get_db_url())
            inspector = inspect(engine)
            schemas = inspector.get_schema_names()
            return schema_name in schemas
        except SQLAlchemyError as e:
            logger.error(f"Error checking if schema exists: {e}")
            return False

    def schema_list(self) -> list:
        """Returns a list of available schemas (databases) in the database."""
        try:
            engine = create_engine(self.get_db_url())
            inspector = inspect(engine)
            schemas = inspector.get_schema_names()
            return schemas
        except SQLAlchemyError as e:
            logger.error(f"Error fetching schema list: {e}")
            return []
