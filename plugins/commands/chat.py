from nonebot import on_message, on_command
from nonebot.adapters import Message, Event, Bot

from nonebot.adapters.discord import Message, MessageSegment, MessageEvent

matcher = on_message(
    priority=11,
    block=False
)

from utils.chatgpt import chat, ChatContext
import random
import chatgame
import asyncio
import logging


@matcher.handle()
async def handle_logger(bot: Bot, event: MessageEvent):
    # Ignore messages with command prefix
    if event.content.startswith('!'):
        return
        
    # get the internal user id based on the event's discord user id
    user_discord_id = event.get_user_id()
    try:
        user_id = await chatgame.get_user_id(user_discord_id)
    except chatgame.UserNotFoundError:
        return

    # get current character
    character_id = await chatgame.get_current_character(user_id)
    if character_id is None:
        await matcher.send(
            message=Message([
                MessageSegment.reference(event.message_id),  # type: ignore
                MessageSegment.text("No character selected yet... please select a character first.")
            ])
        )
        return

    # get current session
    session_id = await chatgame.get_latest_session(user_id, character_id)

    # add user message to the session
    await chatgame.create_new_message(session_id, event.content, user_id, from_user=True)

    # get context from session
    context = await chatgame.get_chat_context(session_id)

    # List of template messages in case of no response
    no_msg = [
        "<Unable to get a response from OPENAI>",
        "I'm having trouble processing that. Let's try again in a moment.",
        "My apologies, I seem to be experiencing technical difficulties.",
    ]

    # Send typing indicator
    await matcher.send(
        message=Message([
            MessageSegment.text("*typing...*")
        ])
    )

    # Try up to 3 times with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            msg = await chat(context)
            if msg:
                await chatgame.create_new_message(session_id, msg, None, from_user=False)
                await matcher.send(
                    message=Message([
                        MessageSegment.text(msg)
                    ])
                )
                return
            else:
                # Wait briefly before retry
                await asyncio.sleep(1 * (2 ** attempt))  # Exponential backoff
        except Exception as e:
            logging.error(f"Error in chat attempt {attempt+1}: {str(e)}")
            if attempt < max_retries - 1:
                # Wait before retry
                await asyncio.sleep(1 * (2 ** attempt))  # Exponential backoff
            else:
                # Last attempt failed
                break

    # If we get here, all attempts failed
    await matcher.send(
        message=Message([
            MessageSegment.reference(event.message_id),
            MessageSegment.text(random.choice(no_msg))
        ])
    )


""""""

# async def permit(event: Event):
#     # TODO: Implement permission check
#     return True
#
# cmd1 = on_command(
#     "memory",
#     priority=10,
#     block=True,
#     permission=permit
# )
#
# @cmd1.handle()
# async def handle_function1():
#     await cmd1.send(str(context.memory))
#
# cmd2 = on_command(
#     "affinity",
#     priority=10,
#     block=True,
#     permission=permit
# )
#
# @cmd2.handle()
# async def handle_function2():
#     await cmd2.send(str(context.affinity))
