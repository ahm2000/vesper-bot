"""Purpose: entry point — creates the bot with only the intents it needs, loads commands/events, logs in.
Run with: python -m src.main   (from the bot/ project root)
"""
import discord
from discord import app_commands
from discord.ext import commands

from . import config, logger
from .command_loader import load_commands
from .event_loader import load_events
from .utils import embeds

intents = discord.Intents.default()
intents.message_content = True  # needed for custom "!command" triggers and edit/delete logging
intents.members = True  # needed for join/leave logging and role assignment

bot = commands.Bot(command_prefix="!", intents=intents, max_messages=200)

load_commands(bot)
load_events(bot)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    logger.error(f"Command \"{interaction.command.name if interaction.command else '?'}\" failed", error)
    payload = {"embed": embeds.error("Something went wrong running that command."), "ephemeral": True}
    try:
        if interaction.response.is_done():
            await interaction.followup.send(**payload)
        else:
            await interaction.response.send_message(**payload)
    except discord.HTTPException:
        pass


if __name__ == "__main__":
    bot.run(config.TOKEN)
