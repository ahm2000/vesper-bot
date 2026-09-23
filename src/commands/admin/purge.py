"""Purpose: bulk-delete recent messages in a channel. Administrator-level server action."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds


def setup(bot: commands.Bot):
    @bot.tree.command(name="purge", description="Bulk delete recent messages in this channel")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.default_permissions(manage_messages=True)
    async def purge(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            embed=embeds.success(
                f"Deleted {len(deleted)} message(s). Messages older than 14 days can't be bulk-deleted by Discord's API."
            )
        )

    return purge
