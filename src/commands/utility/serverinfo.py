"""Purpose: display information about the current server."""
import discord
from discord.ext import commands

from src.utils.embeds import COLORS


def setup(bot: commands.Bot):
    @bot.tree.command(name="serverinfo", description="View information about this server")
    async def serverinfo(interaction: discord.Interaction):
        guild = interaction.guild
        owner = guild.owner or await guild.fetch_member(guild.owner_id)

        embed = discord.Embed(title=guild.name, color=COLORS["primary"])
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=str(owner), inline=True)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:D>", inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="Boost Level", value=str(guild.premium_tier), inline=True)

        await interaction.response.send_message(embed=embed)

    return serverinfo
