"""Purpose: per-guild voice connection, queue, and playback state for the music commands.
Kept as a single in-memory dict — no database needed, and the queue is disposable if the bot restarts.
"""
import asyncio
from dataclasses import dataclass, field

import discord
import yt_dlp

from src import logger

YDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch1",
    "source_address": "0.0.0.0",
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


@dataclass
class Track:
    title: str
    stream_url: str


@dataclass
class GuildMusicState:
    voice_client: discord.VoiceClient
    text_channel: discord.abc.Messageable
    queue: list[Track] = field(default_factory=list)
    loop: bool = False


_states: dict[int, GuildMusicState] = {}


def get_state(guild_id: int) -> GuildMusicState | None:
    return _states.get(guild_id)


async def ensure_state(bot: discord.Client, voice_channel: discord.VoiceChannel, text_channel: discord.abc.Messageable) -> GuildMusicState:
    guild_id = voice_channel.guild.id
    state = _states.get(guild_id)
    if state:
        return state

    voice_client = await voice_channel.connect()
    state = GuildMusicState(voice_client=voice_client, text_channel=text_channel)
    _states[guild_id] = state
    return state


def _extract(query: str) -> Track:
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return Track(title=info.get("title", query), stream_url=info["url"])


async def resolve_track(query: str) -> Track:
    # yt_dlp is blocking (network + subprocess-ish work) — keep it off the event loop.
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _extract, query)


def play_next(bot: discord.Client, guild_id: int) -> None:
    state = _states.get(guild_id)
    if not state:
        return

    if state.loop and state.queue:
        track = state.queue[0]
    elif state.queue:
        track = state.queue.pop(0)
    else:
        asyncio.run_coroutine_threadsafe(_disconnect(guild_id), bot.loop)
        return

    def _after(error: Exception | None):
        if error:
            logger.error(f"Playback error in guild {guild_id}", error)
        bot.loop.call_soon_threadsafe(play_next, bot, guild_id)

    try:
        source = discord.FFmpegPCMAudio(track.stream_url, **FFMPEG_OPTS)
        state.voice_client.play(source, after=_after)
        asyncio.run_coroutine_threadsafe(
            state.text_channel.send(f"🎵 Now playing **{track.title}**"), bot.loop
        )
    except Exception as exc:  # noqa: BLE001 - a bad track shouldn't kill the queue
        logger.error(f"Failed to play track in guild {guild_id}", exc)
        play_next(bot, guild_id)


async def _disconnect(guild_id: int) -> None:
    state = _states.pop(guild_id, None)
    if state and state.voice_client.is_connected():
        await state.voice_client.disconnect()


def destroy_state(bot: discord.Client, guild_id: int) -> None:
    asyncio.run_coroutine_threadsafe(_disconnect(guild_id), bot.loop)
