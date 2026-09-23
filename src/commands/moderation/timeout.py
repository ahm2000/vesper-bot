"""Purpose: temporarily mute (Discord timeout) a member for a set duration."""
import datetime

import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds
from src.utils.case_manager import add_case
from src.utils.permissions import is_moderator

MAX_TIMEOUT_MINUTES = 40320  # Discord's hard cap: 28 days


def setup(bot: commands.Bot):
    @bot.tree.command(name="timeout", description="Temporarily mute a member")
    @app_commands.describe(member="Member to time out", minutes="Duration in minutes (max 40320 = 28 days)", reason="Reason for the timeout")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: app_commands.Range[int, 1, MAX_TIMEOUT_MINUTES], reason: str | None = None):
        if not is_moderator(interaction.user):
            return await interaction.response.send_message(
                embed=embeds.error("You need the Moderate Members permission to use this command."),
                ephemeral=True,
            )

        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                embed=embeds.error("I can't time out that member (role hierarchy)."), ephemeral=True
            )

        await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)

        add_case(str(interaction.guild_id), str(member.id), str(interaction.user.id), f"timeout ({minutes}m)", reason)

        await interaction.response.send_message(
            embed=embeds.success(f"Timed out {member.mention} for {minutes} minute(s) — {reason or 'No reason provided'}")
        )

    return timeout
