import nonebot
from nonebot.adapters.console import Adapter as ConsoleAdapter
from nonebot.adapters.discord import Adapter as DiscordAdapter


# Initialize the NoneBot application
nonebot.init()

# Register the Discord adapter
driver = nonebot.get_driver()
# driver.register_adapter(ConsoleAdapter)
driver.register_adapter(DiscordAdapter)

# Load plugins
nonebot.load_plugins("plugins/commands")

if __name__ == "__main__":
    nonebot.run()