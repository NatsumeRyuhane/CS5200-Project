import logging
import os
import sys
from dotenv import load_dotenv

import nonebot
from nonebot.adapters.console import Adapter as ConsoleAdapter
from nonebot.adapters.discord import Adapter as DiscordAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")

# Load environment variables
load_dotenv()

def init_bot():
    """Initialize the NoneBot application with proper error handling"""
    try:
        # Initialize the NoneBot application
        nonebot.init()
        
        # Register the Discord adapter
        driver = nonebot.get_driver()
        # driver.register_adapter(ConsoleAdapter)
        driver.register_adapter(DiscordAdapter)

        # Verify required environment variables
        if not os.getenv("DISCORD_BOT_TOKEN"):
            logger.error("DISCORD_BOT_TOKEN not found in environment variables")
            sys.exit(1)
            
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not found in environment variables - AI chat will not work")
            
        # Load plugins
        nonebot.load_plugins("plugins/commands")
        
        logger.info("Bot initialization completed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize bot: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if init_bot():
        logger.info("Starting bot...")
        nonebot.run()
    else:
        logger.error("Bot failed to initialize. Exiting.")
        sys.exit(1)