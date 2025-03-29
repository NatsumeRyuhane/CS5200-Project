from utils.MySQLHandler import MySQLHandler

from chatgame.chat import *
from chatgame.exceptions import *

# init Database
db_handler = MySQLHandler.get_instance()
db_handler.initialize()

# Execute SQL initialization file
# db_handler.execute_file("./sql/dbinit.sql")
