# Discord Character Chat Game

A Discord bot that allows users to chat with virtual characters. This project implements a character selection system
with memory, affinity tracking, and customization.

## Features

- Character selection using `!select` command
- Automatic user registration
- Conversation memory tracking
- Character-user relationship (affinity) tracking
- Customizable character details
- Optimized database connection pooling
- Robust error handling and retry mechanisms
- Performance improvements for AI chat

## Setup Instructions

### Installation

This project uses [NoneBot](https://nonebot.dev/) framework and it is recommended to use pipx for installation.

For more details, check the [documentation](https://nonebot.dev/docs/).

1. Install [pipx](https://pipx.pypa.io/stable/)

2. Install NoneBot scaffolding

    ```bash
    pipx install nb-cli
    ```

3. Create a `.env` file from the template and fill in the required environment variables.

4. Run the `main.py` script

    ```bash
    python main.py
    ```

### Environment Variables

The following environment variables are required:

- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_USER`: Database username
- `DATABASE_PASSWORD`: Database password
- `DATABASE_HOST`: Database host
- `DATABASE_PORT`: Database port
- `DATABASE_NAME`: Database name

### For Team Development

#### Option 1: Individual Test Bots

1. Create your own Discord bot in the [Discord Developer Portal](https://discord.com/developers/applications)
2. Enable Message Content Intent under the Bot settings
3. Use your bot's token in your local `.env` file
4. Run the bot locally for testing

### Commands

- `!select <character_name>` - Select a character to chat with

## Technical Improvements

The following optimizations have been implemented:

1. **Database Connection Pooling**:
   - Improved connection validation and reconnection
   - Better error handling for database operations
   - Connection pool with proper resource management

2. **Error Handling and Retry Mechanisms**:
   - Added retry with exponential backoff for OpenAI API calls
   - Better error logging and categorization
   - Type-safe validation for user inputs

3. **Performance Optimizations**:
   - LRU caching for frequently used data
   - Message history management to prevent memory issues
   - Specific error handling for different API error types

4. **Memory Management**:
   - Improved affinity value validation
   - Automatic context pruning to maintain performance
   - Better input validation