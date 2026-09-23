"""Purpose: list all available slash commands grouped by category."""
from collections import defaultdict

import discord
from discord.ext import commands

from src.utils.embeds import COLORS


def setup(bot: commands.Bot):
    @bot.tree.command(name="help", description="List all commands")
    async def help_cmd(interaction: discord.Interaction):
        by_category: dict[str, list[str]] = defaultdict(list)

        for cmd in bot.tree.get_commands():
            category = getattr(cmd, "category", "General")
            by_category[category].append(f"`/{cmd.name}` — {cmd.description}")

        embed = discord.Embed(title="Vesper — Commands", color=COLORS["primary"])
        for category in sorted(by_category):
            embed.add_field(name=category, value="\n".join(by_category[category]), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    return help_cmd
