"""Purpose: handle the roles select menu. Slash commands are dispatched by discord.py's
CommandTree itself, so this only needs to catch the one raw component interaction we use.
"""
import discord
from discord.ext import commands

from src.utils import embeds
from src import logger

# Must match SELECT_ID in src/commands/utility/roles.py. Kept as a plain string (not imported
# from that module) so this event never has to import across the command tree by package path —
# the command loader discovers commands by file path, not by import, so that path may not exist.
SELECT_ID = "vesper-roles-select"

NAME = "on_interaction"


async def execute(bot: commands.Bot, interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return
    if interaction.data.get("custom_id") != SELECT_ID:
        return

    member = interaction.user
    select_component = interaction.message.components[0].children[0]
    all_role_ids = {opt.value for opt in select_component.options}
    selected_role_ids = set(interaction.data.get("values", []))

    to_add = [rid for rid in selected_role_ids if not member.get_role(int(rid))]
    to_remove = [rid for rid in all_role_ids - selected_role_ids if member.get_role(int(rid))]

    try:
        if to_add:
            await member.add_roles(*[interaction.guild.get_role(int(rid)) for rid in to_add])
        if to_remove:
            await member.remove_roles(*[interaction.guild.get_role(int(rid)) for rid in to_remove])
        await interaction.response.send_message(embed=embeds.success("Your roles have been updated."), ephemeral=True)
    except discord.HTTPException as exc:
        logger.error("Failed to update roles from select menu", exc)
        await interaction.response.send_message(
            embed=embeds.error("I couldn't update your roles — check my role position."), ephemeral=True
        )
