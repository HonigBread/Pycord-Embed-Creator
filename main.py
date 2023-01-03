"""
Main Entry for the Bot. This should be the first file to run, any extension will be loaded automatically.
"""

import discord

# Intents all, have to be enabled in Discord Developer Portal
intents = discord.Intents.all()
# Bot Object
bot = discord.Bot(description="Developer Bot for Kissenwelt", owner_id=293827484258926598,
                  debug_guilds=[1026610233335885824], intents=intents)
# Add all developer discord User-IDs
bot.developer = [293827484258926598]

# Add Debug Guilds
bot.debug_guilds = []

# All main Extensions
extensions = ["cogs.embed.embed"]
for extension in extensions:
    bot.load_extension(extension)

# Load Discord Token -> From Discord Developer Portal
with open("./daten/token", "r") as token_file:
    token = token_file.read()

# Check if Bot is online
@bot.listen("on_ready")
async def on_ready() -> None:
    """
    Listener: on_ready

    Listens for on_ready call and prints a statement to signal the successful start of the Bot and connection to the
    Discord API.
    """

    print(f"{bot.user.name} is online")

# Main Entry to Bot-Loop. Everything after will not be executed.
bot.run(token)
