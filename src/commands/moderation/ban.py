"""Purpose: ban a member (or user ID) from the server."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds
from src.utils.case_manager import add_case
from src.utils.permissions import is_moderator


def setup(bot: commands.Bot):
    @bot.tree.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for the ban", delete_days="Delete this many days of their messages (0-7)")
    @app_commands.default_permissions(ban_members=True)
    async def ban(interaction: discord.Interaction, member: discord.User, reason: str | None = None, delete_days: app_commands.Range[int, 0, 7] = 0):
        if not is_moderator(interaction.user):
            return await interaction.response.send_message(
                embed=embeds.error("You need the Ban Members permission to use this command."),
                ephemeral=True,
            )

        await interaction.guild.ban(member, reason=reason, delete_message_seconds=delete_days * 24 * 60 * 60)

        add_case(str(interaction.guild_id), str(member.id), str(interaction.user.id), "ban", reason)

        await interaction.response.send_message(
            embed=embeds.success(f"Banned {member} — {reason or 'No reason provided'}")
        )

    return ban
