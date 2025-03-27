import discord
from discord.ext import commands
import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
load_dotenv()

# connect to MySQL
DATABSE_PASSWORD = os.getenv('DATABASE_PASSWORD')

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

db_config = {
    'host': '35.199.185.202',
    'user': 'root',
    'password': DATABSE_PASSWORD,
    'database': 'db-group8'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='!',intents=intents)



@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

 # choose NPC to talk to
@bot.command()
async def select(ctx, *, character_name):
    """Select a character to talk to by name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Find the character by name
        cursor.execute("SELECT character_id, name, description FROM Virtual_Character WHERE name = %s", (character_name,))
        character = cursor.fetchone()
        
        if not character:
            await ctx.send(f"Character '{character_name}' not found.")
            return
            
        char_id, char_name, description = character
        
        # Get user information
        discord_id = str(ctx.author.id)  
        username = ctx.author.name
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM User WHERE discord_id = %s", (discord_id,))
        user_result = cursor.fetchone()
        
        if not user_result:
            cursor.execute("SELECT MAX(user_id) FROM User")
            result = cursor.fetchone()
            next_id = 1 if result[0] is None else result[0] + 1
            
            # Generate a default email based on Discord username
            default_email = f"{username.lower().replace(' ', '')}_{discord_id}@placeholder.com"
    
            # Insert new user
            cursor.execute(
                "INSERT INTO User (user_id, username, email, discord_id) VALUES (%s, %s, %s, %s)",
                (next_id, username, default_email, discord_id)
            )
            conn.commit()
            
            await ctx.send(f"Welcome, {username}! You've been automatically registered. Now talking with {char_name}...")
            
            # Get the newly created user_id
            user_id = next_id
        else:
            user_id = user_result[0]
        
        # Record this interaction in the Interaction table
        cursor.execute(
            "INSERT INTO Interaction (user_id, character_id, action, context) VALUES (%s, %s, %s, %s)",
            (user_id, char_id, "select", f"User selected {char_name} to talk with")
        )
        
        # Check if a Memory record exists for this user-character pair
        cursor.execute(
            "SELECT summary_text FROM Memory WHERE user_id = %s AND character_id = %s",
            (user_id, char_id)
        )
        memory_record = cursor.fetchone()
        
        if not memory_record:
            # Create initial memory record
            cursor.execute(
                "INSERT INTO Memory (user_id, character_id, summary_text) VALUES (%s, %s, %s)",
                (user_id, char_id, f"First meeting with {username}")
            )
        
        # Check if an Affinity record exists for this user-character pair
        cursor.execute(
            "SELECT value FROM Affinity WHERE user_id = %s AND character_id = %s",
            (user_id, char_id)
        )
        affinity_record = cursor.fetchone()
        
        if not affinity_record:
            # Create initial affinity record
            cursor.execute(
                "INSERT INTO Affinity (user_id, character_id, value) VALUES (%s, %s, %s)",
                (user_id, char_id, 0) 
            )
        
        conn.commit()
        
        # Get customization details if any
        cursor.execute(
            "SELECT attribute, value FROM Customization WHERE character_id = %s",
            (char_id,)
        )
        customizations = cursor.fetchall()
        
        # Create embed for character selection
        embed = discord.Embed(
            title=f"Now talking with {char_name}",
            description=description or f"Hello, I am {char_name}!",
            color=discord.Color.green()
        )
        
        # Add customization details if available
        if customizations:
            custom_details = "\n".join([f"{attr}: {val}" for attr, val in customizations])
            embed.add_field(name="Character Details", value=custom_details, inline=False)
        
        # Add affinity if it exists
        if affinity_record:
            affinity_value = float(affinity_record[0]) * 100  # Convert to percentage
            embed.add_field(name="Relationship", value=f"Affinity: {affinity_value:.1f}%", inline=True)
        
        embed.set_footer(text="Just type messages to chat with this character!")
        
        await ctx.send(embed=embed)
        
    except mysql.connector.Error as err:
        await ctx.send(f"Database error: {err}")
        print(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()
# Run the bot
bot.run(DISCORD_BOT_TOKEN)