"""SQLite setup — moderation cases, custom commands, reminders, per-guild settings.
Uses the stdlib sqlite3 module: no native build step, which keeps the VPS install trivial.
"""
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

_connection = sqlite3.connect(DATA_DIR / "vesper.db", check_same_thread=False)
_connection.row_factory = sqlite3.Row
_connection.execute("PRAGMA journal_mode=WAL")

_connection.executescript(
    """
    CREATE TABLE IF NOT EXISTS mod_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        moderator_id TEXT NOT NULL,
        action TEXT NOT NULL,
        reason TEXT,
        created_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS custom_commands (
        guild_id TEXT NOT NULL,
        name TEXT NOT NULL,
        response TEXT NOT NULL,
        created_by TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        PRIMARY KEY (guild_id, name)
    );

    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        remind_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS guild_settings (
        guild_id TEXT PRIMARY KEY,
        log_channel_id TEXT,
        mute_role_id TEXT
    );
    """
)
_connection.commit()


def get_connection() -> sqlite3.Connection:
    return _connection
