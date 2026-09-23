"""Purpose: runs once on startup — sets bot presence and recovers pending reminders."""
import discord
from discord.ext import commands

from src import logger
from src.utils.reminder_scheduler import recover_reminders

NAME = "on_ready"


async def execute(bot: commands.Bot):
    logger.info(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))
    recover_reminders(bot)
