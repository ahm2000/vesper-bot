"""Purpose: configure which channel Vesper posts logging events (message edits/deletes, joins/leaves) to."""
import discord
from discord import app_commands
from discord.ext import commands

from src.database import get_connection
from src.utils import embeds


def setup(bot: commands.Bot):
    @bot.tree.command(name="setlogchannel", description="Set the channel Vesper posts logs to")
    @app_commands.describe(channel="Channel for logs")
    @app_commands.default_permissions(manage_guild=True)
    async def setlogchannel(interaction: discord.Interaction, channel: discord.TextChannel):
        conn = get_connection()
        conn.execute(
            """INSERT INTO guild_settings (guild_id, log_channel_id) VALUES (?, ?)
               ON CONFLICT(guild_id) DO UPDATE SET log_channel_id = excluded.log_channel_id""",
            (str(interaction.guild_id), str(channel.id)),
        )
        conn.commit()

        await interaction.response.send_message(
            embed=embeds.success(f"Log channel set to {channel.mention}."), ephemeral=True
        )

    return setlogchannel
