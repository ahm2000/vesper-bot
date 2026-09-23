"""Purpose: show the current music queue."""
import discord
from discord.ext import commands

from src.utils import embeds
from src.utils.music_manager import get_state


def setup(bot: commands.Bot):
    @bot.tree.command(name="queue", description="View the current queue")
    async def queue(interaction: discord.Interaction):
        state = get_state(interaction.guild_id)
        if not state or not state.queue:
            return await interaction.response.send_message(embed=embeds.info("The queue is empty."), ephemeral=True)

        listing = "\n".join(f"{i + 1}. {t.title}" for i, t in enumerate(state.queue))
        await interaction.response.send_message(embed=embeds.info(f"**Up next:**\n{listing}"))

    return queue
