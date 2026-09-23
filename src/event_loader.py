"""Purpose: load every event module under src/events and register it as a listener on the bot."""
import importlib
import pkgutil

from discord.ext import commands as discord_commands

from . import events as events_pkg


def load_events(bot: discord_commands.Bot) -> None:
    for _, module_name, is_pkg in pkgutil.iter_modules(events_pkg.__path__):
        if is_pkg:
            continue
        module = importlib.import_module(f"{events_pkg.__name__}.{module_name}")
        if not hasattr(module, "NAME") or not hasattr(module, "execute"):
            continue

        async def _listener(*args, _handler=module.execute, _bot=bot):
            await _handler(_bot, *args)

        bot.add_listener(_listener, module.NAME)
