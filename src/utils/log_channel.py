"""Purpose: shared helper the logging events use to fetch and send to a guild's configured log channel."""
import discord

from src.database import get_connection


async def send_log(guild: discord.Guild, embed: discord.Embed) -> None:
    conn = get_connection()
    row = conn.execute(
        "SELECT log_channel_id FROM guild_settings WHERE guild_id = ?", (str(guild.id),)
    ).fetchone()
    if not row or not row["log_channel_id"]:
        return

    channel = guild.get_channel(int(row["log_channel_id"])) or await guild.fetch_channel(int(row["log_channel_id"]))
    if channel is None or not isinstance(channel, discord.abc.Messageable):
        return

    try:
        await channel.send(embed=embed)
    except discord.HTTPException:
        pass
