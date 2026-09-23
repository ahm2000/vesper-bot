"""Purpose: play a song by URL/search term, or add it to the queue if something is already playing."""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds
from src.utils.music_manager import ensure_state, play_next, resolve_track


def setup(bot: commands.Bot):
    @bot.tree.command(name="play", description="Play a song or add it to the queue")
    @app_commands.describe(query="YouTube URL or search term")
    async def play(interaction: discord.Interaction, query: str):
        voice_state = interaction.user.voice
        if not voice_state or not voice_state.channel:
            return await interaction.response.send_message(
                embed=embeds.error("Join a voice channel first."), ephemeral=True
            )

        await interaction.response.defer()

        track = await resolve_track(query)
        state = await ensure_state(bot, voice_state.channel, interaction.channel)
        state.queue.append(track)

        if not state.voice_client.is_playing():
            play_next(bot, interaction.guild_id)
            return await interaction.followup.send(embed=embeds.success(f"Playing **{track.title}**"))

        await interaction.followup.send(
            embed=embeds.success(f"Added **{track.title}** to the queue (position {len(state.queue)}).")
        )

    return play
