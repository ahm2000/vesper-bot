"""Purpose: set (or clear) the current channel's slowmode/rate limit. Administrator-level server action."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds


def setup(bot: commands.Bot):
    @bot.tree.command(name="slowmode", description="Set this channel's slowmode delay")
    @app_commands.describe(seconds="Delay in seconds (0 to disable, max 21600)")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(interaction: discord.Interaction, seconds: app_commands.Range[int, 0, 21600]):
        await interaction.channel.edit(slowmode_delay=seconds)

        await interaction.response.send_message(
            embed=embeds.success("Slowmode disabled." if seconds == 0 else f"Slowmode set to {seconds} second(s).")
        )

    return slowmode
