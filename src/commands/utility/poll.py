"""Purpose: post a reaction-based poll message with 👍/👎 reactions."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils.embeds import COLORS


def setup(bot: commands.Bot):
    @bot.tree.command(name="poll", description="Create a reaction-based poll")
    @app_commands.describe(question="The poll question")
    async def poll(interaction: discord.Interaction, question: str):
        embed = discord.Embed(title="📊 Poll", description=question, color=COLORS["primary"])
        embed.set_footer(text=f"Started by {interaction.user}")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    return poll
