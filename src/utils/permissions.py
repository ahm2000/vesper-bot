"""Purpose: shared permission checks used by moderation/admin commands."""
import discord


def is_moderator(member: discord.Member) -> bool:
    return member.guild_permissions.moderate_members


def is_admin(member: discord.Member) -> bool:
    return member.guild_permissions.administrator
