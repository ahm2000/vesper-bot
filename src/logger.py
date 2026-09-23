"""Purpose: console logging plus optional Discord webhook alerts on error."""
import datetime
import traceback
import aiohttp

from . import config


def _timestamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def info(message: str) -> None:
    print(f"[INFO] {_timestamp()} {message}")


def warn(message: str) -> None:
    print(f"[WARN] {_timestamp()} {message}")


def error(message: str, exc: BaseException | None = None) -> None:
    print(f"[ERROR] {_timestamp()} {message}")
    if exc is not None:
        traceback.print_exception(exc)

    if not config.ERROR_WEBHOOK_URL:
        return

    stack = "".join(traceback.format_exception(exc)) if exc else ""
    embed = {
        "title": "Vesper error",
        "description": f"```{str(message)[:3800]}```",
        "color": 0xFF3B3B,
        "timestamp": _timestamp(),
    }
    if stack:
        embed["fields"] = [{"name": "Stack", "value": f"```{stack[:1000]}```"}]

    async def _send():
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(config.ERROR_WEBHOOK_URL, json={"embeds": [embed]})
        except Exception:
            # Never let the webhook itself crash the process (e.g. rate limit, deleted webhook).
            pass

    import asyncio

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_send())
    except RuntimeError:
        # No running loop (e.g. error happened before the bot started) — fire and forget synchronously.
        asyncio.run(_send())
