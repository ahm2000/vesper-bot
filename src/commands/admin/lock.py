"""Purpose: lock or unlock the current channel for the default role (@everyone). Administrator-level server action."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds


def setup(bot: commands.Bot):
    @bot.tree.command(name="lock", description="Lock or unlock this channel for @everyone")
    @app_commands.describe(locked="true to lock, false to unlock")
    @app_commands.default_permissions(manage_channels=True)
    async def lock(interaction: discord.Interaction, locked: bool):
        everyone = interaction.guild.default_role
        overwrite = interaction.channel.overwrites_for(everyone)
        overwrite.send_messages = False if locked else None
        await interaction.channel.set_permissions(everyone, overwrite=overwrite)

        await interaction.response.send_message(
            embed=embeds.success("🔒 Channel locked." if locked else "🔓 Channel unlocked.")
        )

    return lock
