"""Purpose: issue a recorded warning to a member without taking further action."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds
from src.utils.case_manager import add_case
from src.utils.permissions import is_moderator


def setup(bot: commands.Bot):
    @bot.tree.command(name="warn", description="Warn a member and record it in their moderation history")
    @app_commands.describe(member="Member to warn", reason="Reason for the warning")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        if not is_moderator(interaction.user):
            return await interaction.response.send_message(
                embed=embeds.error("You need the Moderate Members permission to use this command."),
                ephemeral=True,
            )

        add_case(str(interaction.guild_id), str(member.id), str(interaction.user.id), "warn", reason)

        try:
            await member.send(
                embed=embeds.warn(
                    f"You were warned in **{interaction.guild.name}**.\n**Reason:** {reason or 'No reason provided'}"
                )
            )
        except discord.HTTPException:
            pass  # Member may have DMs disabled — the warning is still recorded server-side.

        await interaction.response.send_message(
            embed=embeds.success(f"Warned {member.mention} — {reason or 'No reason provided'}")
        )

    return warn
