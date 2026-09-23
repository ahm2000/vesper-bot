"""Purpose: register slash commands with Discord. Run after adding/changing any command file.
`python -m src.deploy`          -> registers to DEV_GUILD_ID instantly (use while developing)
`python -m src.deploy --global` -> registers globally (takes up to ~1 hour to propagate; use for production)
"""
import sys

import discord
from discord.ext import commands

from . import config
from .command_loader import load_commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
load_commands(bot)

is_global = "--global" in sys.argv


@bot.event
async def on_ready():
    if is_global:
        synced = await bot.tree.sync()
        print(f"Registered {len(synced)} commands globally.")
    else:
        if not config.DEV_GUILD_ID:
            print("DEV_GUILD_ID is not set — set it in .env, or run with --global to deploy globally.")
            await bot.close()
            return
        guild = discord.Object(id=int(config.DEV_GUILD_ID))
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Registered {len(synced)} commands to guild {config.DEV_GUILD_ID}.")

    await bot.close()


if __name__ == "__main__":
    bot.run(config.TOKEN)
