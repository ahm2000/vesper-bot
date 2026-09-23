"""Purpose: skip the currently playing track."""
import discord
from discord.ext import commands

from src.utils import embeds
from src.utils.music_manager import get_state


def setup(bot: commands.Bot):
    @bot.tree.command(name="skip", description="Skip the current track")
    async def skip(interaction: discord.Interaction):
        state = get_state(interaction.guild_id)
        if not state or not state.voice_client.is_playing():
            return await interaction.response.send_message(embed=embeds.error("Nothing is playing."), ephemeral=True)

        state.voice_client.stop()  # triggers the `after` callback, which advances the queue
        await interaction.response.send_message(embed=embeds.success("Skipped."))

    return skip
