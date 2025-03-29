import logging

import openai
from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Optional

from chatgame import update_memory, update_affinity
from utils.ChatContext import ChatContext

# Load environment variables from .env file
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize OpenAI client with API key from environment variables
client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
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


async def chat(context: ChatContext) -> Optional[str]:
    """
    Send a chat request to the AI model and process the response.

    Args:
        context: ChatContext containing conversation history and character state

    Returns:
        The AI's response text or None if the request failed
    """
    # Construct system prompts to guide the AI's behavior
    system_prompt = [
        {
            "role"   : "system",
            "content": f"""
                You are a role-playing chatbot. You are playing as a character in a role-playing game.
                The following is the character settings for the role you are playing. You should use this information to adjust your responses to the user.
                {context.character_settings}
            """
        },
        {
            "role"   : "system",
            "content": f"""
                The following is the user's character settings. You should use this information to adjust your responses to the user.
                In case of any conflict between the user character settings and your character settings, you should prioritize the user character settings.
                {context.user_character_settings}
            """
        },
        {
            "role"   : "system",
            "content": f"""
                Each time you reply, you can update your `memory` and `affinity` for the user by using the actions field according to the user id.
                You should use the memory field to build impressions of different users and remember them, and you should use the affinity field to remember your affinity for different users.
                The affinity field should be set to an integer value between [0, 100], with 50 being a neutral value.
                You should adjust this value according to the user's interactions with you and whether you like interacting with that user, and change your attitude towards that user accordingly.
                When updating the corresponding fields, use only the user's id and do not include their name.
                
                The following field contains the summary of long-term memory with the user. You should use this information to adjust your responses to the user.
                {context.memory}

                The following field contains the affinity of the user. You should use this information to adjust your responses to the user.
                {context.affinity}
            """
        },
    ]

    try:
        # Send request to OpenAI API with structured response format
        completion = await client.beta.chat.completions.parse(
            messages=system_prompt + context.message_history,
            model="gpt-4o-mini",
            response_format=ChatResponse
        )

        response = completion.choices[0].message.parsed
        if response:
            # Process any actions requested by the AI
            for action in response.actions:
                try:
                    if action.type == ActionType.affinity:
                        await update_affinity(context.user_id, context.character_id, int(action.value))
                    elif action.type == ActionType.memory:
                        await update_memory(context.user_id, context.character_id, action.value)
                except Exception:
                    logging.WARNING("Failed to update memory or affinity in parsing", exc_info=True)
                    pass

        return str(response.message)
    except Exception:
        # log the exception
        logging.WARNING("ChatGPT API request failed", exc_info=True)
        pass

    return None
