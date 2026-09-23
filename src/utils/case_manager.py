"""Purpose: record and look up moderation cases (warn/timeout/kick/ban history) in SQLite."""
import time

from src.database import get_connection


def add_case(guild_id: str, user_id: str, moderator_id: str, action: str, reason: str | None) -> None:
    conn = get_connection()
    conn.execute(
        """INSERT INTO mod_cases (guild_id, user_id, moderator_id, action, reason, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (guild_id, user_id, moderator_id, action, reason or "No reason provided", int(time.time() * 1000)),
    )
    conn.commit()


def get_cases(guild_id: str, user_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM mod_cases WHERE guild_id = ? AND user_id = ?
           ORDER BY created_at DESC LIMIT 25""",
        (guild_id, user_id),
    ).fetchall()
    return [dict(row) for row in rows]
