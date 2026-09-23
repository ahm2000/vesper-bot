"""Purpose: post a self-assignable roles menu (dropdown) members can use to opt in/out of roles.
Selection is handled generically in src/events/on_interaction.py (matched by custom_id), so this
menu keeps working even after a bot restart — no per-message state needs to be stored.
"""
import discord
from discord import app_commands
from discord.ext import commands

from src.utils import embeds

SELECT_ID = "vesper-roles-select"


def setup(bot: commands.Bot):
    @bot.tree.command(name="roles", description="Post a self-assignable roles menu")
    @app_commands.describe(role1="Role 1", role2="Role 2", role3="Role 3", role4="Role 4", role5="Role 5")
    @app_commands.default_permissions(manage_roles=True)
    async def roles(
        interaction: discord.Interaction,
        role1: discord.Role,
        role2: discord.Role | None = None,
        role3: discord.Role | None = None,
        role4: discord.Role | None = None,
        role5: discord.Role | None = None,
    ):
        chosen = [r for r in (role1, role2, role3, role4, role5) if r is not None]

        bot_top_role = interaction.guild.me.top_role
        too_high = next((r for r in chosen if r.position >= bot_top_role.position), None)
        if too_high:
            return await interaction.response.send_message(
                embed=embeds.error(f"My highest role must be above **{too_high.name}** for me to assign it."),
                ephemeral=True,
            )

        select = discord.ui.Select(
            custom_id=SELECT_ID,
            placeholder="Select your roles",
            min_values=0,
            max_values=len(chosen),
            options=[discord.SelectOption(label=r.name, value=str(r.id)) for r in chosen],
        )
        view = discord.ui.View(timeout=None)
        view.add_item(select)

        await interaction.channel.send(
            embed=embeds.info("**Self-assignable roles**\nPick the roles you want from the menu below."),
            view=view,
        )
        await interaction.response.send_message(embed=embeds.success("Roles menu posted."), ephemeral=True)

    return roles
