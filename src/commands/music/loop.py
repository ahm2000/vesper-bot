"""Purpose: toggle looping the current track."""
import discord
from discord.ext import commands

from src.utils import embeds
from src.utils.music_manager import get_state


def setup(bot: commands.Bot):
    @bot.tree.command(name="loop", description="Toggle looping the current track")
    async def loop(interaction: discord.Interaction):
        state = get_state(interaction.guild_id)
        if not state:
            return await interaction.response.send_message(embed=embeds.error("Nothing is playing."), ephemeral=True)

        state.loop = not state.loop
        await interaction.response.send_message(
            embed=embeds.success(f"Loop {'enabled' if state.loop else 'disabled'}.")
        )

    return loop
