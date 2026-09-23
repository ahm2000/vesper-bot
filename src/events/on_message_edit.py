"""Purpose: log edited messages to the configured log channel."""
import discord
from discord.ext import commands

from src.utils.embeds import COLORS
from src.utils.log_channel import send_log

NAME = "on_message_edit"


async def execute(bot: commands.Bot, before: discord.Message, after: discord.Message):
    if not after.guild or (after.author and after.author.bot):
        return
    if before.content == after.content:
        return

    embed = discord.Embed(title="✏️ Message edited", color=COLORS["primary"])
    embed.add_field(name="Author", value=str(after.author), inline=True)
    embed.add_field(name="Channel", value=after.channel.mention, inline=True)
    embed.add_field(name="Before", value=before.content or "*No cached content*", inline=False)
    embed.add_field(name="After", value=after.content or "*Empty*", inline=False)

    await send_log(after.guild, embed)
