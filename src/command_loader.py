"""Purpose: auto-discover and register every command module under src/commands — no manual
registration, no __init__.py required. Drop a new .py file into an existing category folder, or
create a brand-new folder with .py files in it, and it's picked up on the next bot start.
The category shown in /help is inferred from the immediate parent folder name.
"""
import importlib.util
import sys
from pathlib import Path

from discord.ext import commands as discord_commands

COMMANDS_DIR = Path(__file__).resolve().parent / "commands"


def _import_file(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_commands(bot: discord_commands.Bot) -> None:
    category_dirs = sorted(
        p for p in COMMANDS_DIR.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))
    )

    for category_dir in category_dirs:
        category_label = category_dir.name[0].upper() + category_dir.name[1:]

        command_files = sorted(
            f for f in category_dir.glob("*.py") if not f.name.startswith("_")
        )
        for file_path in command_files:
            module = _import_file(f"vesper_cmd_{category_dir.name}_{file_path.stem}", file_path)
            if not hasattr(module, "setup"):
                continue

            registered = module.setup(bot)
            for cmd in registered if isinstance(registered, (list, tuple)) else [registered]:
                if cmd is not None:
                    cmd.category = category_label
