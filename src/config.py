"""Loads and validates environment variables from .env."""
import os
from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


TOKEN = _required("DISCORD_TOKEN")
CLIENT_ID = _required("CLIENT_ID")
DEV_GUILD_ID = os.environ.get("DEV_GUILD_ID") or None
ERROR_WEBHOOK_URL = os.environ.get("ERROR_WEBHOOK_URL") or None
OWNER_ID = os.environ.get("OWNER_ID") or None
