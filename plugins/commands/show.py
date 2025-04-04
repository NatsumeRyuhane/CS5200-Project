from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.params import CommandArg
from nonebot.adapters.discord import Message, MessageSegment, MessageEvent

from typing import List, Dict, Any, Optional
import chatgame

# Create command handlers for different show commands
show_chars = on_command("show.characters", aliases={"show characters"}, priority=10, block=True)
show_chars_current = on_command("show.characters.current",
                                aliases={"show characters current"},
                                priority=10,
                                block=True)
show_chars_created = on_command("show.characters.created",
                                aliases={"show characters created"},
                                priority=10,
                                block=True)
show_chars_history = on_command("show.characters.history",
                                aliases={"show characters history"},
                                priority=10,
                                block=True)

show_points = on_command("show.points", aliases={"show points"}, priority=10, block=True)
show_points_history = on_command("show.points.history",
                                 aliases={"show points history"},
                                 priority=10,
                                 block=True)


# Individual command handlers
async def handle_characters_current(user_id: str):
    """Handle 'show characters current' command"""
    character_id = await chatgame.get_current_character(user_id)
    if character_id:
        character = await chatgame.get_character_info(character_id)
        return f"Current character: {character['name']}"
    return "You're not currently chatting with any character."


async def handle_characters_created(user_id: str):
    """Handle 'show characters created' command"""
    created = await chatgame.get_created_characters(user_id)
    if created:
        chars = "\n".join([f"- {char['name']}: {char['character_id']}" for char in created])
        return f"Characters you've created:\n{chars}"
    return "You haven't created any characters yet."


async def handle_characters_history(user_id: str):
    """Handle 'show characters history' command"""
    history = await chatgame.get_character_history(user_id)
    if history:
        chars = "\n".join([f"- {char['name']}: {char['character_id']}" for char in history])
        return f"Characters you've interacted with:\n{chars}"
    return "No character interaction history found."


async def handle_points(user_id: str):
    """Handle 'show points' command"""
    balance = await chatgame.get_points_balance(user_id)
    return f"Your points balance: {balance}"


async def handle_points_history(user_id: str):
    pass
    # To be implemented when chatgame.get_points_history is available


# Command handlers
@show_chars_current.handle()
async def show_chars_current_handler(bot: Bot, event: MessageEvent):
    user_id = await chatgame.get_user_id(event.get_user_id())
    response = await handle_characters_current(user_id)
    await show_chars_current.send(
        message=Message([
            MessageSegment.reference(event.message_id),
            MessageSegment.text(response)
        ])
    )


@show_chars_created.handle()
async def show_chars_created_handler(bot: Bot, event: MessageEvent):
    user_id = await chatgame.get_user_id(event.get_user_id())
    response = await handle_characters_created(user_id)
    await show_chars_created.send(
        message=Message([
            MessageSegment.reference(event.message_id),
            MessageSegment.text(response)
        ])
    )


@show_chars_history.handle()
async def show_chars_history_handler(bot: Bot, event: MessageEvent):
    user_id = await chatgame.get_user_id(event.get_user_id())
    response = await handle_characters_history(user_id)
    await show_chars_history.send(
        message=Message([
            MessageSegment.reference(event.message_id),
            MessageSegment.text(response)
        ])
    )


@show_chars.handle()
async def show_chars_handler(bot: Bot, event: MessageEvent):
    user_id = await chatgame.get_user_id(event.get_user_id())
    response = await handle_characters_current(user_id)
    await show_chars.send(
        message=Message([
            MessageSegment.reference(event.message_id),
            MessageSegment.text(response)
        ])
    )


@show_points.handle()
async def show_points_handler(bot: Bot, event: MessageEvent):
    user_id = await chatgame.get_user_id(event.get_user_id())
    response = await handle_points(user_id)
    await show_points.send(
        message=Message([
            MessageSegment.reference(event.message_id),
            MessageSegment.text(response)
        ])
    )


@show_points_history.handle()
async def show_points_history_handler(bot: Bot, event: MessageEvent):
    user_id = await chatgame.get_user_id(event.get_user_id())
    # When implemented, use handle_points_history instead
    response = "Points history feature is not yet available."
    await show_points_history.send(
        message=Message([
            MessageSegment.reference(event.message_id),
            MessageSegment.text(response)
        ])
    )
