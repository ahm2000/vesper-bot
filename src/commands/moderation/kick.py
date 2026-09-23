"""Purpose: remove a member from the server (they can rejoin with a new invite)."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds
from src.utils.case_manager import add_case
from src.utils.permissions import is_moderator


def setup(bot: commands.Bot):
    @bot.tree.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for the kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick(interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        if not is_moderator(interaction.user):
            return await interaction.response.send_message(
                embed=embeds.error("You need the Kick Members permission to use this command."),
                ephemeral=True,
            )

        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                embed=embeds.error("I can't kick that member (role hierarchy)."), ephemeral=True
            )

        tag = str(member)
        await member.kick(reason=reason)

        add_case(str(interaction.guild_id), str(member.id), str(interaction.user.id), "kick", reason)

        await interaction.response.send_message(
            embed=embeds.success(f"Kicked {tag} — {reason or 'No reason provided'}")
        )

    return kick
