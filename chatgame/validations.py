from utils.MySQLHandler import MySQLHandler
from chatgame.exceptions import *

def validate_user_id(user_id: str) -> bool:
    # Get the database handler instance
    db = MySQLHandler.get_instance().initialize()

    # check if user id exists in database
    result = db.fetch_one(
        "SELECT user_id FROM User WHERE user_id = %s", (user_id,))

    if result is None:
        raise UserNotFoundError("User ID not found in database")

    return True

def validate_character_id(character_id: str) -> bool:
    # Get the database handler instance
    db = MySQLHandler.get_instance().initialize()

    # check if character id exists in database
    result = db.fetch_one(
        "SELECT character_id FROM Virtual_Character WHERE character_id = %s", (character_id,))

    if result is None:
        raise CharacterNotFoundError("Character ID not found in database")

    return True

def validate_session_id(session_id: str) -> bool:
    # Get the database handler instance
    db = MySQLHandler.get_instance().initialize()

    # check if session id exists in database
    result = db.fetch_one(
        "SELECT session_id FROM Chat_Session WHERE session_id = %s", (session_id,))

    if result is None:
        raise SessionNotFoundError("Session ID not found in database")

    return True