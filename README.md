# Vesper — Discord Bot (Python / discord.py)

Source lives in `src/`, organized by purpose:

```
src/
  main.py                Entry point — creates the bot, loads commands/events, logs in
  deploy.py               Registers slash commands with Discord (run manually after changes)
  config.py               Reads and validates .env
  database.py              SQLite setup (moderation cases, custom commands, reminders, settings)
  logger.py                Console logging + optional Discord webhook alerts on error
  command_loader.py        Loads every module under commands/ and registers it on the bot's tree
  event_loader.py          Loads every module under events/ as a listener on the bot
  commands/
    moderation/            warn, timeout, kick, ban, cases — member-targeted moderation
    admin/                 purge, slowmode, lock, setlogchannel — server/channel-level actions
    messaging/              announce, embed — bot sends a message/embed somewhere on your behalf
    utility/                 poll, remind, roles, serverinfo, help
    music/                   play, skip, queue, loop
    custom/                  customcommand — create/edit/delete/list server custom text commands
  events/                  on_ready, on_message, on_message_delete, on_message_edit,
                           on_member_join, on_member_remove, on_interaction — each is one
                           Discord event, one job
  utils/                   shared helpers (embeds, permissions, case_manager, music_manager,
                           reminder_scheduler, log_channel)
data/                      SQLite database file lives here at runtime (gitignored)
banner/                    drop your server banner art here (not referenced by code)
```

Every command module has a one-line docstring at the top stating its purpose, plus its own slash
command `description=` (shown in Discord's UI and in `/help`).

Built on **discord.py** (the standard, actively maintained Python Discord library) and the stdlib
`sqlite3` module — no native compilation step for the database at all, which keeps the VPS install
about as simple as it gets.

## Adding new commands — zero configuration

`command_loader.py` auto-discovers everything under `src/commands/` at startup. You never register
a command by hand, and nothing needs an `__init__.py`:

- **Adding a command to an existing category** (e.g. another utility command): drop a new `.py` file
  into `src/commands/utility/` following the same `setup(bot)` pattern as the files next to it.
  Restart the bot (`pm2 restart vesper`) and it's loaded. Run `python -m src.deploy --global` (or
  `python -m src.deploy` for instant testing) so Discord actually shows the new slash command —
  that registration step is unavoidable, it's how Discord itself learns the command exists.
- **Adding a whole new category** (e.g. a `fun/` folder of meme commands): just create
  `src/commands/fun/` and put `.py` files in it. No `__init__.py`, no touching `command_loader.py`,
  no edits anywhere else. The folder name becomes the category label shown in `/help` automatically
  (`fun` → **Fun**).
- **The only two things every command file needs**: a `setup(bot)` function that defines the command
  with `@bot.tree.command(...)` and returns it, matching the shape of any existing file (copy
  `src/commands/utility/poll.py` as the simplest template). Look at that file's imports if your
  command needs a permission check, the shared embed helpers, or the database.

Same for events: any new file dropped into `src/events/` defining `NAME` (a discord.py event name
like `"on_message"`) and an `async def execute(bot, ...)` is picked up automatically — see
`src/events/on_ready.py` as the simplest example.

## A note on resources (1 vCPU / 1 GB RAM)

This is genuinely tight for a Discord bot with music. Moderation, logging, utility, and custom
commands are lightweight — text in, text out, a small SQLite file. **Music is the one feature that
can actually strain this box**: audio decoding/streaming is the most CPU- and memory-intensive thing
a bot does, and if two people queue songs in different servers at once on a 1-vCPU box, expect
stutter. The code here is written to be as light as possible (capped message cache, minimal gateway
intents, audio extraction offloaded to a thread pool so it doesn't block the event loop), but
there's a real ceiling. If it becomes a problem, the two normal fixes are: upgrade to 2 vCPU / 2 GB,
or disable the music commands and run everything else (that's most of what a moderation/utility bot
actually needs day to day).

---

## 1. Create the bot in Discord's Developer Portal

1. Go to https://discord.com/developers/applications → **New Application** → name it "Vesper".
2. Left sidebar → **Bot** → **Reset Token** → copy it. This is `DISCORD_TOKEN`. Treat it like a
   password — anyone with it fully controls your bot.
3. On the same Bot page, enable these under **Privileged Gateway Intents**:
   - **Server Members Intent** (needed for join/leave logging and role assignment)
   - **Message Content Intent** (needed for custom `!command` triggers and edit/delete logging)
4. Left sidebar → **General Information** → copy the **Application ID**. This is `CLIENT_ID`.
5. Left sidebar → **OAuth2** → **URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot permissions: at minimum `Send Messages`, `Manage Messages`, `Manage Roles`, `Kick Members`,
     `Ban Members`, `Moderate Members`, `Connect`, `Speak`, `Read Message History`, `Embed Links`.
   - Copy the generated URL — that's your **invite link**. Use it to add the bot to your test server,
     and it's the same link you'll put behind the "Add to Discord" button on the website.

## 2. Set up the `.env` file

Copy `.env.example` to `.env` and fill in:

```
DISCORD_TOKEN=your-bot-token-from-step-1
CLIENT_ID=your-application-id-from-step-1
DEV_GUILD_ID=your-test-server-id      # optional, see below
ERROR_WEBHOOK_URL=                    # optional, see "Webhooks" below
OWNER_ID=                             # optional, your own Discord user ID
```

To get a server ID or your own user ID: in Discord, enable **Settings → Advanced → Developer Mode**,
then right-click a server or your name and **Copy Server/User ID**.

**Never commit `.env`** — it's already in `.gitignore`.

## 3. Webhooks (error alerts)

This is optional but recommended. Discord webhooks let the bot post a message to a channel without
needing a bot user — here it's used purely so you get pinged in Discord when something crashes,
instead of only finding out from server logs.

1. In your Discord server, go to a channel (e.g. `#bot-logs`) → **Edit Channel → Integrations →
   Webhooks → New Webhook**.
2. Copy the **Webhook URL** and put it in `.env` as `ERROR_WEBHOOK_URL`.
3. That's it — `src/logger.py` posts there automatically when `logger.error(...)` is called
   anywhere in the code.

This is separate from the bot's own log channel (`/setlogchannel`), which is for message
edits/deletes and member joins/leaves — set that up in Discord after the bot is running.

## 4. VPS setup (Ubuntu/Debian assumed — adjust package manager if different)

SSH into your VPS, then:

```bash
# System update
sudo apt update && sudo apt upgrade -y

# Python 3.11, venv, build tools, ffmpeg (ffmpeg is required at runtime by the music commands
# to transcode/stream audio into voice channels), and git
sudo apt install -y python3.11 python3.11-venv python3-pip ffmpeg git

python3.11 --version   # should print Python 3.11.x
```

Create a **non-root user** to run the bot under (skip if you already have one):

```bash
sudo adduser vesper
sudo usermod -aG sudo vesper   # optional, only if this user needs sudo
su - vesper
```

Get the code onto the VPS. Either `git clone` your repo, or `scp`/`rsync` the `bot/` folder up:

```bash
# from your local machine, adjust the path/host
scp -r "D:\Vesper BOT\bot" youruser@your-vps-ip:~/vesper-bot
```

Then on the VPS, set up a virtual environment and install dependencies:

```bash
cd ~/vesper-bot
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
nano .env    # fill in DISCORD_TOKEN, CLIENT_ID, etc. from steps 1-3 above
```

## 5. Register slash commands

Slash commands must be registered with Discord separately from running the bot — this only needs
to be re-run when you add/change a command:

```bash
source .venv/bin/activate

# Instant, but only visible in one server — good for testing (set DEV_GUILD_ID in .env first)
python -m src.deploy

# Visible in every server the bot is in — takes up to ~1 hour to fully propagate.
# Use this once things are confirmed working.
python -m src.deploy --global
```

## 6. Run the bot persistently with PM2

`python -m src.main` run directly dies when your SSH session closes. Use PM2 (a Node-based process
manager, but it manages any process — including Python — just as well) so the bot survives
disconnects, restarts on crash, and restarts on server reboot:

```bash
# PM2 itself needs Node.js/npm, even though the bot is Python
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

cd ~/vesper-bot
pm2 start ".venv/bin/python" --name vesper --interpreter none --max-memory-restart 400M -- -m src.main
```

`--interpreter none` tells PM2 not to try running the script with its own Node interpreter — we're
handing it a Python binary directly. `--max-memory-restart 400M` is a safety net: if something leaks
memory and creeps toward your 1 GB ceiling, PM2 restarts the process cleanly instead of the whole VPS
running out of memory and the OS OOM-killing something important.

Make PM2 itself survive a VPS reboot:

```bash
pm2 startup    # run the command it prints (needs sudo)
pm2 save
```

Useful PM2 commands:

```bash
pm2 logs vesper       # tail logs live
pm2 restart vesper    # after pulling code changes
pm2 stop vesper
pm2 status
```

**Alternative without PM2/Node**, if you'd rather keep this pure Python: use a `systemd` service
instead — ask if you want a ready-made unit file for that; it does the same job (survives
disconnects, restarts on crash/reboot) without pulling in Node.js at all.

## 7. Updating the bot later

```bash
cd ~/vesper-bot
git pull            # or re-upload changed files
source .venv/bin/activate
pip install -r requirements.txt   # only if requirements.txt changed
python -m src.deploy --global     # only if you added/changed a slash command
pm2 restart vesper
```

## 8. Basic VPS hardening (do this once, early)

```bash
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

The bot makes only outbound connections to Discord's (and YouTube's, for music) API — you don't need
to open any inbound ports for it to work.
