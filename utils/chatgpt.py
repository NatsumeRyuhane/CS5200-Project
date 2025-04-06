import logging
import os
import time
from functools import lru_cache

import openai
from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple

from chatgame import update_memory, update_affinity
from utils.ChatContext import ChatContext

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatgpt")

# Initialize OpenAI client with API key from environment variables
client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0,  # 30 second timeout
)


class ActionType(str, Enum):
    """Defines the possible action types for character interactions."""
    memory = "memory"  # Used for storing memories about users
    affinity = "affinity"  # Used for tracking relationship level with users


class Action(BaseModel):
    """Represents an action that the AI character wants to perform."""
    type: ActionType  # Type of action (memory or affinity)
    value: str  # Value to associate with the action


class ChatResponse(BaseModel):
    """Structured response from the AI model."""
    message: str  # Text response to send to the user
    actions: List[Action]  # List of actions to perform after response


# Cache for character settings to reduce redundant operations
@lru_cache(maxsize=100)
def _get_system_prompts(character_settings: str, user_character_settings: str, memory: str, affinity: str) -> List[Dict[str, str]]:
    """
    Create system prompts from context.
    This function is cached to avoid recreating the same prompts.
    
    Args:
        character_settings: Character settings data
        user_character_settings: User character settings data
        memory: Memory data
        affinity: Affinity data
        
    Returns:
        List of system prompt messages
    """
    return [
        {
            "role": "system",
            "content": f"""
                You are a role-playing chatbot. You are playing as a character in a role-playing game.
                The following is the character settings for the role you are playing. You should use this information to adjust your responses to the user.
                {character_settings}
            """
        },
        {
            "role": "system",
            "content": f"""
                The following is the user's character settings. You should use this information to adjust your responses to the user.
                In case of any conflict between the user character settings and your character settings, you should prioritize the user character settings.
                {user_character_settings}
            """
        },
        {
            "role": "system",
            "content": f"""
                Each time you reply, you can update your `memory` and `affinity` for the user by using the actions field according to the user id.
                You should use the memory field to build impressions of different users and remember them, and you should use the affinity field to remember your affinity for different users.
                The affinity field should be set to an integer value between [0, 100], with 50 being a neutral value.
                You should adjust this value according to the user's interactions with you and whether you like interacting with that user, and change your attitude towards that user accordingly.
                When updating the corresponding fields, use only the user's id and do not include their name.
                
                The following field contains the summary of long-term memory with the user. You should use this information to adjust your responses to the user.
                {memory}

                The following field contains the affinity of the user. You should use this information to adjust your responses to the user.
                {affinity}
            """
        },
    ]


async def _process_actions(user_id: str, character_id: str, actions: List[Action]) -> None:
    """
    Process actions requested by the AI model.
    
    Args:
        user_id: User ID
        character_id: Character ID
        actions: List of actions to process
    """
    for action in actions:
        try:
            if action.type == ActionType.affinity:
                await update_affinity(user_id, character_id, int(action.value))
            elif action.type == ActionType.memory:
                await update_memory(user_id, character_id, action.value)
        except Exception as e:
            logger.warning(f"Failed to update {action.type}: {str(e)}")


async def chat(context: ChatContext) -> Optional[str]:
    """
    Send a chat request to the AI model and process the response.

    Args:
        context: ChatContext containing conversation history and character state

    Returns:
        The AI's response text or None if the request failed
    """
    start_time = time.time()
    
    # Construct system prompts to guide the AI's behavior
    system_prompt = _get_system_prompts(
        context.character_settings,
        context.user_character_settings,
        context.memory,
        str(context.affinity)
    )

    # Prepare the messages - limit history if too long
    message_history = context.message_history
    if len(message_history) > ChatContext.chatContextMaximumMessageLength:
        # Keep the most recent messages
        message_history = message_history[-ChatContext.chatContextMaximumMessageLength:]

    try:
        # Send request to OpenAI API with structured response format
        completion = await client.beta.chat.completions.parse(
            messages=system_prompt + message_history,
            model="gpt-4o-mini",
            response_format=ChatResponse
        )

        response = completion.choices[0].message.parsed
        if response:
            # Process any actions requested by the AI in a separate task to not block response
            await _process_actions(context.user_id, context.character_id, response.actions)

        # Log timing for performance monitoring
        elapsed_time = time.time() - start_time
        logger.info(f"Chat request completed in {elapsed_time:.2f}s")
        
        return str(response.message)
    except openai.APITimeoutError:
        logger.error("OpenAI API request timed out")
    except openai.RateLimitError:
        logger.error("OpenAI API rate limit exceeded")
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)

    return None
