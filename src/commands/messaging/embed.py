"""Purpose: have the bot send a formatted embed message to a chosen channel."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds as embed_helpers


def setup(bot: commands.Bot):
    @bot.tree.command(name="embed", description="Send a formatted embed as Vesper to a channel")
    @app_commands.describe(channel="Channel to send to", title="Embed title", description="Embed body text")
    @app_commands.default_permissions(manage_guild=True)
    async def embed_cmd(interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str):
        sent_embed = discord.Embed(title=title, description=description, color=embed_helpers.COLORS["primary"])
        await channel.send(embed=sent_embed)
        await interaction.response.send_message(
            embed=embed_helpers.success(f"Embed sent to {channel.mention}."), ephemeral=True
        )

    return embed_cmd
