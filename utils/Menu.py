import argparse

from utils.ServerManager import ServerManager


def run():
    """Function to handle database connection based on user CLI input."""
    parser = argparse.ArgumentParser(description='Database Connection Manager')
    parser.add_argument('--database', type=str, required=True, help='The name of the database to connect to')
    connection = ""
    args = parser.parse_args()

    db_manager = ServerManager()

    try:
        connection = db_manager.connect_to_server()
    finally:
        db_manager.close_connection(connection)
