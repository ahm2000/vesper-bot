"""Purpose: create, edit, delete, and list server-specific custom text commands.
Custom commands are triggered by prefix (default "!") — see src/events/on_message.py.
"""
import time

import discord
from discord import app_commands
from discord.ext import commands

from src.database import get_connection
from src.utils import embeds


def setup(bot: commands.Bot):
    group = app_commands.Group(
        name="customcommand",
        description="Manage this server's custom commands",
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @group.command(name="create", description="Create a custom command")
    @app_commands.describe(name="Command name (no prefix)", response="What the bot replies with")
    async def create(interaction: discord.Interaction, name: str, response: str):
        await _upsert(interaction, name, response)

    @group.command(name="edit", description="Edit an existing custom command")
    @app_commands.describe(name="Command name", response="New response")
    async def edit(interaction: discord.Interaction, name: str, response: str):
        await _upsert(interaction, name, response)

    @group.command(name="delete", description="Delete a custom command")
    @app_commands.describe(name="Command name")
    async def delete(interaction: discord.Interaction, name: str):
        conn = get_connection()
        cursor = conn.execute(
            "DELETE FROM custom_commands WHERE guild_id = ? AND name = ?",
            (str(interaction.guild_id), name.lower()),
        )
        conn.commit()

        embed = (
            embeds.success(f"Custom command `!{name.lower()}` deleted.")
            if cursor.rowcount
            else embeds.error(f"No custom command named `{name.lower()}`.")
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @group.command(name="list", description="List all custom commands")
    async def list_cmd(interaction: discord.Interaction):
        conn = get_connection()
        rows = conn.execute(
            "SELECT name FROM custom_commands WHERE guild_id = ? ORDER BY name",
            (str(interaction.guild_id),),
        ).fetchall()

        embed = (
            embeds.info(f"**Custom commands:**\n{', '.join(f'`!{r[0]}`' for r in rows)}")
            if rows
            else embeds.info("No custom commands set up yet.")
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _upsert(interaction: discord.Interaction, name: str, response: str):
        conn = get_connection()
        conn.execute(
            """INSERT INTO custom_commands (guild_id, name, response, created_by, created_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(guild_id, name) DO UPDATE SET response = excluded.response, created_by = excluded.created_by""",
            (str(interaction.guild_id), name.lower(), response, str(interaction.user.id), int(time.time() * 1000)),
        )
        conn.commit()
        await interaction.response.send_message(
            embed=embeds.success(f"Custom command `!{name.lower()}` saved."), ephemeral=True
        )

    bot.tree.add_command(group)
    return group
