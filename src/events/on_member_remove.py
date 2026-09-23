"""Purpose: log members leaving to the configured log channel."""
import discord
from discord.ext import commands

from src.utils.embeds import COLORS
from src.utils.log_channel import send_log

NAME = "on_member_remove"


async def execute(bot: commands.Bot, member: discord.Member):
    embed = discord.Embed(
        title="📤 Member left",
        description=f"{member} ({member.id})",
        color=COLORS["error"],
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    await send_log(member.guild, embed)
