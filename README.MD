# Discord Character Chat Game

A Discord bot that allows users to chat with virtual characters. This project implements a character selection system with memory, affinity tracking, and customization.

## Features

- Character selection using `!select` command
- Automatic user registration
- Conversation memory tracking
- Character-user relationship (affinity) tracking
- Customizable character details

## Setup Instructions
### Installation
1. 
```bash
pip install -r requirements.txt
```
2.Create a `.env` file from the template:
3.Fill in environment variables

### For Team Development

#### Option 1: Individual Test Bots
1. Create your own Discord bot in the [Discord Developer Portal](https://discord.com/developers/applications)
2. Enable Message Content Intent under the Bot settings
3. Use your bot's token in your local `.env` file
4. Run the bot locally for testing

### Running the Bot

```bash
python chatgame.py
```

### Commands

- `!select <character_name>` - Select a character to chat with