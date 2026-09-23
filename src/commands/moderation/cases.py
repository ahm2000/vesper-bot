"""Purpose: look up a member's moderation history within this server."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds
from src.utils.case_manager import get_cases
from src.utils.permissions import is_moderator


def setup(bot: commands.Bot):
    @bot.tree.command(name="cases", description="View a member's moderation history")
    @app_commands.describe(member="Member to look up")
    @app_commands.default_permissions(moderate_members=True)
    async def cases(interaction: discord.Interaction, member: discord.User):
        if not is_moderator(interaction.user):
            return await interaction.response.send_message(
                embed=embeds.error("You need the Moderate Members permission to use this command."),
                ephemeral=True,
            )

        history = get_cases(str(interaction.guild_id), str(member.id))
        if not history:
            return await interaction.response.send_message(
                embed=embeds.info(f"{member} has a clean record."), ephemeral=True
            )

        lines = [
            f"**#{c['id']}** `{c['action']}` — {c['reason']}\n<t:{c['created_at'] // 1000}:R> by <@{c['moderator_id']}>"
            for c in history
        ]
        embed = discord.Embed(
            title=f"Moderation history — {member}",
            description="\n\n".join(lines),
            color=embeds.COLORS["primary"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    return cases
