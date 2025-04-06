from typing import Optional, List, Dict, Any


class ChatContext:
    """Manages conversation context and character state."""

    # Constants for context management
    chatContextMaximumMessageLength: int = 100  # Default maximum message length
    DEFAULT_AFFINITY: int = 50  # Default affinity value

    def __init__(
            self,
            user_id: str = "",
            character_id: str = "",
            message_history: Optional[List[Dict[str, str]]] = None,
            memory: str = "",
            affinity: int = DEFAULT_AFFINITY,
            character_settings: str = "",
            user_character_settings: Optional[Any] = "") -> None:
        """
        Initialize a new chat context.

        Args:
            user_id: The ID of the user.
            character_id: The ID of the character.
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
        self.affinity = self._validate_affinity(affinity)  # Character's affinity levels with users
        self.character_settings = character_settings  # AI character's personality/settings
        self.user_character_settings = user_character_settings  # User's additional character settings (appending to AI's settings)
    
    def _validate_affinity(self, affinity: int) -> int:
        """
        Validates the affinity value to ensure it's within acceptable range.
        
        Args:
            affinity: The affinity value to validate
            
        Returns:
            The validated affinity value
        """
        try:
            affinity_value = int(affinity)
            # Ensure affinity is within range
            return max(0, min(100, affinity_value))
        except (ValueError, TypeError):
            # If conversion fails, return default
            return self.DEFAULT_AFFINITY
            
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender ("user" or "assistant")
            content: The content of the message
        """
        self.message_history.append({
            "role": role,
            "content": content
        })
        
        # Trim history if it exceeds the maximum length
        if len(self.message_history) > self.chatContextMaximumMessageLength:
            # Keep the most recent messages
            self.message_history = self.message_history[-self.chatContextMaximumMessageLength:]
            
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.message_history = []
        
    def update_memory(self, new_memory: str) -> None:
        """
        Update the character's memory about the user.
        
        Args:
            new_memory: The new memory to store
        """
        self.memory = new_memory
        
    def update_affinity(self, new_affinity: int) -> None:
        """
        Update the character's affinity with the user.
        
        Args:
            new_affinity: The new affinity value
        """
        self.affinity = self._validate_affinity(new_affinity)
