from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.discord import Message, MessageSegment, MessageEvent

# Create simple command handler
register_cmd = on_command("register", aliases={".register"}, priority=10, block=True)

import chatgame

@register_cmd.handle()
async def command_handler(bot: Bot, event: MessageEvent):
    try:
        await chatgame.register_user(event.get_user_id(), event.author.global_name)
        await register_cmd.send(
            message=Message([
                MessageSegment.reference(event.message_id),
                MessageSegment.text(f"Successfully registered user {event.author.global_name}.")
            ])
        )
    except chatgame.UserAlreadyExistsError:
        uid = await chatgame.get_user_id(event.get_user_id())
        await register_cmd.send(
            message=Message([
                MessageSegment.reference(event.message_id),
                MessageSegment.text(f"User already registered with uid {uid}")
            ])
        )
        return
    except chatgame.UserNotFoundError as e:
        await register_cmd.send(
            message=Message([
                MessageSegment.reference(event.message_id),
                MessageSegment.text(f"Error registering user: {str(e)}")
            ])
        )
        return
