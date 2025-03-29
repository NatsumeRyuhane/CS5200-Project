class CharacterNotFoundError(Exception):
    """Custom exception for character not found in the database."""
    pass

class UserNotFoundError(Exception):
    """Custom exception for user not found in the database."""
    pass

class SessionNotFoundError(Exception):
    """Custom exception for session not found in the database."""
    pass

class UserAlreadyExistsError(Exception):
    """Custom exception for user already exists in the database."""
    pass