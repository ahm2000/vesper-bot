"""Purpose: have the bot send a plain announcement message to a chosen channel."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds


def setup(bot: commands.Bot):
    @bot.tree.command(name="announce", description="Send an announcement as Vesper to a channel")
    @app_commands.describe(channel="Channel to send to", message="Message content")
    @app_commands.default_permissions(manage_guild=True)
    async def announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        await channel.send(content=message)
        await interaction.response.send_message(
            embed=embeds.success(f"Announcement sent to {channel.mention}."), ephemeral=True
        )

    return announce
