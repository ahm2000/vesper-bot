"""Purpose: schedule reminder deliveries and recover any pending ones after a restart."""
import asyncio
import time

import discord

from src import logger
from src.database import get_connection
from . import embeds


def _schedule_delivery(bot: discord.Client, reminder_id: int, channel_id: str, user_id: str, message: str, remind_at_ms: int) -> None:
    delay = max((remind_at_ms - int(time.time() * 1000)) / 1000, 0)

    async def _deliver():
        await asyncio.sleep(delay)
        conn = get_connection()
        try:
            channel = bot.get_channel(int(channel_id)) or await bot.fetch_channel(int(channel_id))
            if isinstance(channel, discord.abc.Messageable):
                await channel.send(content=f"<@{user_id}>", embed=embeds.info(f"⏰ Reminder: {message}"))
        except Exception as exc:  # noqa: BLE001 - a failed delivery should never crash the bot
            logger.warn(f"Failed to deliver reminder {reminder_id}: {exc}")
        finally:
            conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()

    bot.loop.create_task(_deliver())


def add_reminder(bot: discord.Client, guild_id: str, channel_id: str, user_id: str, message: str, remind_at_ms: int) -> None:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO reminders (guild_id, channel_id, user_id, message, remind_at)
           VALUES (?, ?, ?, ?, ?)""",
        (guild_id, channel_id, user_id, message, remind_at_ms),
    )
    conn.commit()
    _schedule_delivery(bot, cursor.lastrowid, channel_id, user_id, message, remind_at_ms)


def recover_reminders(bot: discord.Client) -> None:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM reminders WHERE remind_at > ?", (int(time.time() * 1000),)).fetchall()
    for row in rows:
        _schedule_delivery(bot, row["id"], row["channel_id"], row["user_id"], row["message"], row["remind_at"])
    if rows:
        logger.info(f"Recovered {len(rows)} pending reminder(s).")
