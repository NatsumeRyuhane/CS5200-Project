from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.rule import ArgumentParser
from nonebot.adapters.discord import Message, MessageSegment, MessageEvent
from nonebot.params import CommandArg

import chatgame

# Create command handler
select_cmd = on_command("select", aliases={".select"}, priority=10, block=True)

@select_cmd.handle()
async def command_handler(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    # Get the character_id from message arguments
    character_id = args.extract_plain_text().strip()
    
    if not character_id:
        await select_cmd.send(
            message=Message([
                MessageSegment.reference(event.message_id),
                MessageSegment.text("Please provide a character ID.")
            ])
        )
        return
    
    # Get the internal user id based on the event's discord user id
    user_discord_id = event.get_user_id()
    try:
        user_id = await chatgame.get_user_id(user_discord_id)
    except chatgame.UserNotFoundError:
        await select_cmd.send(
            message=Message([
                MessageSegment.reference(event.message_id),
                MessageSegment.text(f"User not found. Please register first.")
            ])
        )
        return

    # Try to select the character
    try:
        await chatgame.change_current_character(user_id, character_id)
        character = await chatgame.get_character_info(character_id)
        if character is None:
            await select_cmd.send(
                message=Message([
                    MessageSegment.reference(event.message_id),
                    MessageSegment.text(f"Character '{character_id}' not found.")
                ])
            )
            return
        
        # Send success message if everything works
        await select_cmd.send(
            message=Message([
                MessageSegment.reference(event.message_id),
                MessageSegment.text(f"Character '{character['name']}' selected successfully.")
            ])
        )
    except Exception as e:
        await select_cmd.send(
            message=Message([
                MessageSegment.reference(event.message_id),
                MessageSegment.text(f"Error selecting character: {str(e)}")
            ])
        )
