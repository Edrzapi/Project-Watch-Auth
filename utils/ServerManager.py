import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, QueuePool
from sqlalchemy.orm import sessionmaker, scoped_session

from utils.DatabaseConfig import DatabaseConfig
from utils.LoggingConfig import LoggerManager
import threading

# Load environment variables
load_dotenv()

# Initialize logger
logger = LoggerManager().get_logger()


class ServerManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Singleton
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ServerManager, cls).__new__(cls)
                cls._instance._init_once(*args, **kwargs)
        return cls._instance

    def _init_once(self, secret_name=None, region_name=None):
        # Only run once to initialize variables
        if not hasattr(self, 'initialized'):
            self.secret_name = secret_name or os.getenv('SECRET_NAME')
            self.region_name = region_name or os.getenv('REGION_NAME')
            self.secret = self.get_secret(os.getenv('SECRET_NAME'))
            self.config = DatabaseConfig(self.secret)

            # Session and engine setup
            self.engine = None
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False)
            self.scoped_session = None
            self.initialized = True

    def create_engine(self, schema_name=None):
        """Creates a SQLAlchemy engine, optionally for a specific schema."""

        # Generate the database URL using the DatabaseConfig class
        db_url = self.config.get_db_url(schema_name)

        try:
            # Create and return the SQLAlchemy engine
            engine = create_engine(
                db_url,  # The database URL for connection
                poolclass=QueuePool,  # Use QueuePool for connection pooling
                pool_size=10,  # The number of connections to keep open in the pool
                max_overflow=20,  # The maximum number of connections to create beyond pool_size
                echo=True  # Log all SQL statements (useful for debugging)
            )
            logger.info(f"Successfully created SQLAlchemy engine for schema: {schema_name}")
            return engine
        except Exception as e:
            # Log the error message if engine creation fails
            logger.error(f"Failed to create SQLAlchemy engine: {e}")
            raise e  # Re-raise the exception after logging

    def set_schema(self, schema_name=None):
        """Initialize the default schema on app startup."""
        if schema_name:
            logger.info(f"Setting default schema to: {schema_name}")
            self.switch_schema(schema_name)
        else:
            raise RuntimeError("No default schema provided.")

    def switch_schema(self, schema_name: str):
        """Switches to a different schema."""
        try:
            logger.info(f"Switching to schema: {schema_name}")
            self.close_session()
            if self.engine:
                self.engine.dispose()  # Dispose of the current engine (unbind)
            self.engine = self.create_engine(schema_name)
            self.SessionLocal.configure(bind=self.engine)
            self.scoped_session = scoped_session(self.SessionLocal)
            logger.info(f"Successfully switched to schema: {schema_name}")
        except Exception as e:
            logger.error(f"Failed to switch to schema {schema_name}: {e}")
            raise RuntimeError(f"Error switching to schema: {schema_name}") from e

    def get_session(self):
        """Retrieves a new session from the current engine."""
        if self.scoped_session is None:
            raise RuntimeError("No database engine set. Call 'switch_schema' first.")
        return self.scoped_session()

    def close_session(self):
        """Closes and removes the current session."""
        if self.scoped_session:
            self.scoped_session.remove()

    def get_secret(self, secret_name):
        """Retrieves the secret from AWS Secrets Manager."""
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=self.region_name)

        try:
            response = client.get_secret_value(SecretId=str(secret_name))
            secret = response.get('SecretString', '{}')
            logger.info("Successfully retrieved secret from AWS Secrets Manager.")
            return json.loads(secret)
        except ClientError as e:
            logger.error(f"Failed to retrieve secret: {e}")
            raise RuntimeError("Error retrieving secret from AWS Secrets Manager.") from e
