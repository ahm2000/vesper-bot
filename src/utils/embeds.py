"""Purpose: shared color palette and quick-build embeds used across every command."""
import discord

COLORS = {
    "primary": 0xA855F7,
    "success": 0x22D3EE,
    "error": 0xFF4D4D,
    "warn": 0xFFB020,
}


def success(description: str) -> discord.Embed:
    return discord.Embed(description=f"✅ {description}", color=COLORS["success"])


def error(description: str) -> discord.Embed:
    return discord.Embed(description=f"❌ {description}", color=COLORS["error"])


def warn(description: str) -> discord.Embed:
    return discord.Embed(description=f"⚠️ {description}", color=COLORS["warn"])


def info(description: str) -> discord.Embed:
    return discord.Embed(description=description, color=COLORS["primary"])
