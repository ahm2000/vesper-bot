"""Purpose: set a personal reminder that the bot delivers back in this channel later."""
import time

import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds
from src.utils.reminder_scheduler import add_reminder


def setup(bot: commands.Bot):
    @bot.tree.command(name="remind", description="Set a reminder")
    @app_commands.describe(minutes="Remind me in this many minutes (max 10080 = 7 days)", message="What to remind you about")
    async def remind(interaction: discord.Interaction, minutes: app_commands.Range[int, 1, 10080], message: str):
        remind_at_ms = int(time.time() * 1000) + minutes * 60 * 1000

        add_reminder(bot, str(interaction.guild_id), str(interaction.channel_id), str(interaction.user.id), message, remind_at_ms)

        await interaction.response.send_message(
            embed=embeds.success(f"Got it — I'll remind you here <t:{remind_at_ms // 1000}:R>."), ephemeral=True
        )

    return remind
