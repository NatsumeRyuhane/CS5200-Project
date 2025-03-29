import uuid
from typing import Optional, List, Union, Dict

from utils.ChatContext import ChatContext
from utils.MySQLHandler import get_db_handler, MySQLHandler
from chatgame.validations import *


async def get_user_id(discord_id: str) -> str:
    """
    Get the user ID from the database using Discord ID.

    Args:
        discord_id: The Discord ID of the user.

    Returns:
        The user ID (UUID string).

    Raises:
        UserNotFoundError: If the user is not found in the database.
    """
    db = get_db_handler()
    result = db.fetch_one(
        "SELECT user_id FROM User WHERE discord_id = %s", (discord_id,))
    if result is None:
        raise UserNotFoundError("User not found")

    return result["user_id"]


async def register_user(discord_id: str, username: str) -> None:
    """
    Register a new user in the database.

    Args:
        discord_id: The Discord ID of the user.
        username: The username of the user (Discord display name).

    Raises:
        UserAlreadyExistsError: If the user already exists in the database.
        UserNotFoundError: If the user registration fails or validation fails.
    """
    db = get_db_handler()
    # Check if user already exists
    result = db.fetch_one(
        "SELECT user_id FROM User WHERE discord_id = %s", (discord_id,))
    if result is not None:
        raise UserAlreadyExistsError("User already exists")

    # Generate a new UUID for the user
    uid = str(uuid.uuid4())

    # Insert new user into the database
    db.execute(
        "INSERT INTO User (user_id, discord_id, username) VALUES (%s, %s, %s)",
        (uid, discord_id, username))

    # Validate the user was created correctly
    validate_user_id(uid)


async def get_chat_context(session_id) -> ChatContext:
    """
    Get the chat context for a user and character in a particular session.

    Args:
        session_id: The ID of the session.

    Returns:
        The ChatContext object containing all relevant session data.

    Raises:
        SessionNotFoundError: If the session is not found in the database.
    """
    db = get_db_handler()
    validate_session_id(session_id)

    # Get user_id and character_id from database for given session_id
    result = db.fetch_one(
        "SELECT * FROM Chat_Session WHERE session_id = %s", (session_id,))
    if result is None:
        raise SessionNotFoundError("Session not found")

    character_id = result["character_id"]
    user_id = result["user_id"]

    # Get message history from database for given session_id (most recent first)
    message_history = []
    result = db.fetch_all(
        "SELECT * FROM Message WHERE session_id = %s ORDER BY timestamp DESC LIMIT %s",
        (session_id, ChatContext.chatContextMaximumMessageLength))
    for message in result:
        role = "user" if message["from_user"] else "assistant"
        if role == "user":
            user_id = message["from_user"]
            user_name = await get_username(user_id)
            message_history.append({
                "role"   : role,
                "content": f"{user_name}<{user_id}>\n" + message["content"]
            })
        else:
            message_history.append({
                "role"   : role,
                "content": message["content"]
            })

    # Get memory (long-term context) from database
    result = db.fetch_one(
        "SELECT summary_text FROM Memory WHERE user_id = %s AND character_id = %s",
        (user_id, character_id))
    memory = result["summary_text"] if result else ""

    # Get character configuration from database
    result = db.fetch_one(
        "SELECT settings FROM Virtual_Character WHERE character_id = %s", (character_id,))
    character_settings = result["settings"] if result else ""

    # Get affinity level (relationship value) from database
    result = db.fetch_one(
        "SELECT value FROM Affinity WHERE user_id = %s AND character_id = %s",
        (user_id, character_id))
    affinity = result["value"] if result else 50  # Default affinity is 50

    # Get user-specific character customizations from database
    result = db.fetch_one(
        "SELECT attribute, value FROM Customization WHERE user_id = %s AND character_id = %s",
        (user_id, character_id))
    user_character_settings = []
    if result is not None:
        for user_settings in result:
            user_character_settings.append({
                "attribute": user_settings["attribute"],
                "value"    : user_settings["value"]
            })

    # Create and return chat context with all gathered information
    chat_context = ChatContext(
        user_id=user_id,
        character_id=character_id,
        message_history=message_history,
        memory=memory,
        affinity=affinity,
        character_settings=character_settings,
        user_character_settings=user_character_settings
    )

    return chat_context


async def get_latest_session(user_id: str, character_id: str) -> str:
    """
    Find the latest session ID for a user and character or create a new one if none exists.

    Args:
        user_id: The ID of the user.
        character_id: The ID of the character.

    Returns:
        The session ID (either existing or newly created).

    Raises:
        UserNotFoundError: If the user is not found in the database.
        CharacterNotFoundError: If the character is not found in the database.
    """
    db = get_db_handler()
    validate_user_id(user_id)
    validate_character_id(character_id)

    result = db.fetch_one(
        "SELECT session_id FROM Chat_Session WHERE user_id = %s AND character_id = %s ORDER BY start_time DESC LIMIT 1",
        (user_id, character_id))

    if result is None:
        # Create a new session if none exists
        return await create_new_session(user_id, character_id)

    return result['session_id']


async def create_new_session(user_id: str, character_id: str) -> str:
    """
    Create a new chat session for a user and character.
    :param user_id:
    :param character_id:
    :return:
    """
    db = get_db_handler()
    validate_user_id(user_id)
    validate_character_id(character_id)

    # Create a new session
    sid = str(uuid.uuid4())
    db.execute(
        "INSERT INTO Chat_Session (session_id, user_id, character_id) VALUES (%s, %s, %s)",
        (sid, user_id, character_id))
    return sid


async def update_affinity(user_id: str, character_id: str, affinity: int) -> None:
    """
    Update the affinity level for a user and character, or create it if it doesn't exist.

    Args:
        user_id: The ID of the user.
        character_id: The ID of the character.
        affinity: The new affinity level (0-100).

    Raises:
        UserNotFoundError: If the user is not found in the database.
        CharacterNotFoundError: If the character is not found in the database.
    """
    db = get_db_handler()
    validate_user_id(user_id)
    validate_character_id(character_id)

    # Try to update existing record, if none exists, create a new one
    rows_affected = db.execute(
        "UPDATE Affinity SET value = %s WHERE user_id = %s AND character_id = %s",
        (affinity, user_id, character_id))
    if rows_affected == 0:
        db.execute(
            "INSERT INTO Affinity (user_id, character_id, value) VALUES (%s, %s, %s)",
            (user_id, character_id, affinity))


async def update_memory(user_id: str, character_id: str, memory: str) -> None:
    """
    Update the memory for a user and character, or create it if it doesn't exist.

    Args:
        user_id: The ID of the user.
        character_id: The ID of the character.
        memory: The new memory text (long-term context).

    Raises:
        UserNotFoundError: If the user is not found in the database.
        CharacterNotFoundError: If the character is not found in the database.
    """
    db = get_db_handler()
    validate_user_id(user_id)
    validate_character_id(character_id)

    # Try to update existing record, if none exists, create a new one
    rows_affected = db.execute(
        "UPDATE Memory SET summary_text = %s WHERE user_id = %s AND character_id = %s",
        (memory, user_id, character_id))
    if rows_affected == 0:
        db.execute(
            "INSERT INTO Memory (user_id, character_id, summary_text) VALUES (%s, %s, %s)",
            (user_id, character_id, memory))


async def get_current_character(user_id: str) -> Optional[str]:
    """
    Get the current selected character ID for a user.

    Args:
        user_id: The ID of the user.

    Returns:
        The character ID of the most recently interacted character, or None if no interactions.
    """
    db = get_db_handler()
    result = db.fetch_one(
        "SELECT current_character FROM User WHERE user_id = %s",
        (user_id,))
    if result is None:
        return None
    return result["current_character"]


async def change_current_character(user_id: str, character_id: str) -> None:
    """
    Change the current character for a user.

    Args:
        user_id: The ID of the user.
        character_id: The ID of the character to set as current.

    Raises:
        UserNotFoundError: If the user is not found in the database.
        CharacterNotFoundError: If the character is not found in the database.
    """
    db = get_db_handler()
    validate_user_id(user_id)
    validate_character_id(character_id)

    # Update the current character for the user
    db.execute(
        "UPDATE User SET current_character = %s WHERE user_id = %s",
        (character_id, user_id))


async def get_created_characters(user_id: str) -> List[str]:
    """
    Get the list of characters created by the user.

    Args:
        user_id: The ID of the user.

    Returns:
        A list of character IDs created by the user, or empty list if none.
    """
    db = get_db_handler()
    result = db.fetch_all(
        "SELECT character_id FROM Virtual_Character WHERE creator_id = %s", (user_id,))
    if result is None:
        return []
    return [character["character_id"] for character in result]


async def get_character_history(user_id: str) -> List[Dict[str, str]]:
    """
    Get the list of characters interacted with by the user.

    Args:
        user_id: The ID of the user.

    Returns:
        A list of dictionaries containing character information (name and ID),
        ordered by most recent interaction.
    """
    db = get_db_handler()
    chars = []

    result = db.fetch_all(
        "SELECT DISTINCT character_id FROM Interaction WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
    if result is None:
        return []

    for char in result:
        try:
            validate_character_id(char["character_id"])
        except UserNotFoundError:
            continue

        character_name = db.fetch_one(
            "SELECT name FROM Virtual_Character WHERE character_id = %s", (char["character_id"],))

        c = {
            "name"        : character_name["name"],
            "character_id": char["character_id"]
        }
        chars.append(c)

    return chars


async def get_points_balance(user_id: str) -> int:
    """
    Get the current points balance for a user.

    Args:
        user_id: The ID of the user.

    Returns:
        The current points balance as an integer.

    Raises:
        UserNotFoundError: If the user is not found in the database.
    """
    db = get_db_handler()
    validate_user_id(user_id)

    result = db.fetch_one(
        "SELECT points_balance FROM User WHERE user_id = %s", (user_id,))
    return result["points_balance"]


async def get_points_history(origin_user_id: str) -> List[Dict[str, str]]:
    """
    Get the points transaction history for a user.

    Args:
        origin_user_id: The ID of the user whose transaction history to retrieve.

    Returns:
        A list of transaction dictionaries containing transaction details,
        ordered by most recent first.

    Raises:
        UserNotFoundError: If the user is not found in the database.
    """
    db = get_db_handler()
    validate_user_id(origin_user_id)
    history = []

    result = db.fetch_all(
        "SELECT sender_id, receiver_id, amount, time FROM Transaction WHERE sender_id = %s ORDER BY time DESC",
        (origin_user_id,))
    if result is None:
        return []
    else:
        for transaction in result:
            t = {
                "sender_id"  : transaction["sender_id"],
                "receiver_id": transaction["receiver_id"],
                "amount"     : transaction["amount"],
                "time"       : transaction["time"]
            }

            history.append(t)

    return history


async def get_character_info(character_id: str) -> Dict[str, Union[str, int]]:
    """
    Get character information from the database.

    Args:
        character_id: The ID of the character.

    Returns:
        A dictionary containing character information (name, description, etc.).

    Raises:
        CharacterNotFoundError: If the character is not found in the database.
    """
    db = get_db_handler()
    validate_character_id(character_id)

    result = db.fetch_one(
        "SELECT * FROM Virtual_Character WHERE character_id = %s", (character_id,))
    if result is None:
        raise CharacterNotFoundError("Character not found")

    return {
        "name"        : result["name"],
        "character_id": result["character_id"],
        "description" : result["description"],
        "creator_id"  : result["creator_id"],
        "settings"    : result["settings"],
        "creation_time": result["creation_time"]
    }


async def create_new_message(session_id: str, content: str, author_id: str, from_user: bool) -> None:
    """
    Create a new message in the database.

    Args:
        session_id: The ID of the chat session.
        content: The content of the message.
        from_user: Whether the message is from the user or the character.

    Raises:
        SessionNotFoundError: If the session is not found in the database.
    """
    db = get_db_handler()
    validate_session_id(session_id)

    if not from_user:
        author_id = None

    # Insert new message into the database
    msgid = str(uuid.uuid4())
    db.execute(
        "INSERT INTO Message (session_id, message_id, from_user, content) VALUES (%s, %s, %s, %s)",
        (session_id, msgid, author_id if author_id is not None else None, content))


async def get_username(user_id):
    """
    Get the username for a given user ID.

    Args:
        user_id: The ID of the user.

    Returns:
        The username of the user.

    Raises:
        UserNotFoundError: If the user is not found in the database.
    """
    db = get_db_handler()
    validate_user_id(user_id)

    result = db.fetch_one(
        "SELECT username FROM User WHERE user_id = %s", (user_id,))
    if result is None:
        raise UserNotFoundError("User not found")

    return result["username"]
