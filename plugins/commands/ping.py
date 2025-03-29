from typing import Union

from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.discord import Message, MessageSegment, MessageEvent, GuildMessageCreateEvent

# Use a simpler on_command approach instead of Alconna
ping = on_command("ping", aliases={".ping"}, priority=10, block=True)

@ping.handle()
async def handle_ping(bot: Bot, event: MessageEvent):
    await ping.send(
        message=Message([
            MessageSegment.reference(event.message_id),
            MessageSegment.text("Pong!")
        ])
    )