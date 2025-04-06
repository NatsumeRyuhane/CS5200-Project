import os

import mysql.connector
from mysql.connector import pooling
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from functools import wraps
from os import getenv
from dotenv import load_dotenv


def sql_transaction(func):
    """
    Decorator to execute a function within a SQL transaction context.
    - Automatically gets connection from pool
    - Commits on success
    - Rolls back on exception
    - Always closes cursor and connection
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        connection = None
        cursor = None
        try:
            connection = self.pool.get_connection()
            
            # Validate connection is active
            if not connection.is_connected():
                connection.reconnect(attempts=3, delay=1)
                
            cursor = connection.cursor(dictionary=True)
            
            # Start transaction
            connection.start_transaction()

            # Pass the cursor and connection to the function
            result = func(self, cursor, connection, *args, **kwargs)

            # If function executes successfully, commit
            connection.commit()
            return result
        except mysql.connector.Error as e:
            # Log the error
            print(f"Database error: {e}")
            # If any error occurs, rollback
            if connection and connection.is_connected():
                connection.rollback()
            raise e
        except Exception as e:
            # If any error occurs, rollback
            if connection and connection.is_connected():
                connection.rollback()
            raise e
        finally:
            # Always close cursor and connection
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    return wrapper


class MySQLHandler:
    """
    Handler for MySQL database operations with connection pooling.
    Implemented as a singleton.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MySQLHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, pool_name: str = "mysql_pool", pool_size: int = 5):
        """
        Initialize MySQL handler with connection pooling

        Args:
            pool_name: Name of the connection pool
            pool_size: Number of connections in the pool
        """
        # Skip initialization if already done
        if getattr(self, "_initialized", False):
            return

        self.pool_name = pool_name
        self.pool_size = pool_size
        self.pool = None
        self.config = {}

        # Mark as initialized
        self._initialized = True

    def initialize(self):
        """Initialize connection pool with configuration"""
        self._load_config_from_env()
        self._initialize_pool()
        return self

    def _load_config_from_env(self):
        """Load database configuration from environment variables"""
        # Load environment variables
        load_dotenv()

        # Get database configuration from environment variables
        self.config = {
            "user"    : getenv("DATABASE_USER", "root"),
            "password": getenv("DATABASE_PASSWORD", "12345678"),
            "host"    : getenv("DATABASE_HOST", "localhost"),
            "port"    : getenv("DATABASE_PORT", "3306"),
            "database": getenv("DATABASE_NAME", "CS5200"),
            "pool_reset_session": True,  # Reset session variables when connection returns to pool
            "pool_recycle": 3600,        # Recycle connections after 1 hour
            "connect_timeout": 10        # Connection timeout in seconds
        }

    def _initialize_pool(self):
        """Initialize the connection pool with current configuration"""
        if self.pool:
            # Close existing connections if pool exists
            try:
                self.pool._remove_connections()
            except:
                pass

        # Create connection pool
        self.pool = pooling.MySQLConnectionPool(
            pool_name=self.pool_name,
            pool_size=self.pool_size,
            **self.config
        )

    def update_config(self, config: Dict[str, Any]):
        """
        Update database configuration and reinitialize the connection pool

        Args:
            config: Dictionary with configuration parameters to update
        """
        self.config.update(config)
        self._initialize_pool()
        return self

    def check_connection(self) -> bool:
        """
        Check if database connection is working
        
        Returns:
            True if connection is working, False otherwise
        """
        connection = None
        try:
            connection = self.pool.get_connection()
            return connection.is_connected()
        except Exception:
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()

    @sql_transaction
    def execute(self, cursor, connection, query: str, params: Optional[Union[Tuple, Dict]] = None) -> int:
        """
        Execute a query that doesn't return data (INSERT, UPDATE, DELETE)

        Args:
            cursor: Database cursor (provided by decorator)
            connection: Database connection (provided by decorator)
            query: SQL query string
            params: Parameters for the query

        Returns:
            Number of affected rows
        """
        cursor.execute(query, params)
        return cursor.rowcount

    @sql_transaction
    def execute_file(self, cursor, connection, file_path):
        """
        Execute SQL commands from a file

        Args:
            cursor: Database cursor (provided by decorator)
            connection: Database connection (provided by decorator)
            file_path (str): Path to the SQL file
        """
        # Convert relative path to absolute if needed
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SQL file not found: {file_path}")

        with open(file_path, 'r') as f:
            content = f.read().strip()

        if not content:
            raise ValueError(f"SQL file is empty: {file_path}")

        # Split commands by semicolon and filter out empty ones
        commands = [cmd.strip() for cmd in content.split(';') if cmd.strip()]

        if not commands:
            raise ValueError(f"No valid SQL commands found in: {file_path}")

        for command in commands:
            if command:  # Additional check to ensure command isn't empty
                cursor.execute(command)


    @sql_transaction
    def fetch_one(self, cursor, connection, query: str, params: Optional[Union[Tuple, Dict]] = None) -> Optional[
        Dict[str, Any]]:
        """
        Fetch a single row from the database

        Args:
            cursor: Database cursor (provided by decorator)
            connection: Database connection (provided by decorator)
            query: SQL query string
            params: Parameters for the query

        Returns:
            A dictionary with column names as keys, or None if no rows found
        """
        cursor.execute(query, params)
        return cursor.fetchone()


    @sql_transaction
    def fetch_all(self, cursor, connection, query: str, params: Optional[Union[Tuple, Dict]] = None) -> List[
        Dict[str, Any]]:
        """
        Fetch all rows from the database

        Args:
            cursor: Database cursor (provided by decorator)
            connection: Database connection (provided by decorator)
            query: SQL query string
            params: Parameters for the query

        Returns:
            A list of dictionaries with column names as keys
        """
        cursor.execute(query, params)
        return cursor.fetchall()

    # Global instance accessor - fixed to be a class method
    @classmethod
    def get_db_handler(cls) -> 'MySQLHandler':
        """
        Get the global MySQLHandler instance

        Returns:
            The singleton instance of MySQLHandler
        """
        return cls.get_instance()

# This function can also be used outside the class if needed
def get_db_handler() -> MySQLHandler:
    """
    Get the global MySQLHandler instance

    Returns:
        The singleton instance of MySQLHandler
    """
    return MySQLHandler.get_instance()
