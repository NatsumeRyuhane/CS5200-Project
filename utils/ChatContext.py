from typing import Optional, List, Dict


class ChatContext:
    """Manages conversation context and character state."""

    chatContextMaximumMessageLength: int = 100  # Default maximum message length

    def __init__(
            self,
            user_id: str = "",
            character_id: str = "",
            message_history: Optional[List[Dict[str, str]]] = None,
            memory: str = "",
            affinity: int = 50,
            character_settings: str = "",
            user_character_settings: Optional[List[Dict[str, str]]] = "") -> None:
        """
        Initialize a new chat context.

        Args:
            user_id: The ID of the user.
            message_history: The conversation history.
            memory: Character's memories about users.
            affinity: Character's affinity levels with users.
            character_settings: AI character's personality/settings.
            user_character_settings: User's additional character settings (appending to AI's settings).
        """
        self.user_id = user_id  # User ID
        self.character_id = character_id  # Character ID
        self.message_history = message_history if message_history is not None else []  # Conversation history
        self.memory = memory  # Character's memories about users
        self.affinity = affinity  # Character's affinity levels with users
        self.character_settings = character_settings  # AI character's personality/settings
        self.user_character_settings = user_character_settings  # User's additional character settings (appending to AI's settings)
