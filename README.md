# QueueNotifier — Installation Guide

## Requirements

- World of Warcraft (Retail)
- [Python 3.8+](https://www.python.org/downloads/)
- A Telegram account

---

## Step 1 — Create a Telegram Bot

1. Open Telegram and message **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the **bot token** it gives you (e.g. `123456789:ABC-abc_abcd`)
4. Send any message to your new bot through Telegram.
5. Open this URL in a browser:
   ```
   https://api.telegram.org/bot{TOKEN_FROM_STEP_3}/getUpdates
   ```
   For example the URL would look like (keep 'bot' in the url and add the token right next to it):
   ```
   https://api.telegram.org/bot123456789:ABC-abc_abcd/getUpdates
   ```
6. Find the `"id"` field inside `"chat"` — this is your **Chat ID** (_If you see an empty response although you have sent a message to your bot then wait a couple of minutes for it to update_)

---

## Step 2 — Install the WoW Addon

Copy the `addon/QueueNotifier/` folder into your AddOns directory:

**macOS**
```
/Applications/World of Warcraft/_retail_/Interface/AddOns/
```

**Windows**
```
C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\
```

Launch WoW, go to the **AddOns** menu on the character select screen, and enable **Queue Notifier**.

> If WoW flags the addon as out of date, run `/run print(GetBuildInfo())` in-game and update the interface number on line 1 of `QueueNotifier.toc`.

---

## Step 3 — Run the Companion App

**macOS** — double-click `run_mac.command`
> On first run, right-click → Open to bypass Gatekeeper.

**Windows** — double-click `run_windows.bat`

On first launch you will be prompted for your bot token and chat ID. The app will auto-detect your WoW installation, send a test message to confirm everything works, and save your config for future runs.

Leave the companion app running in the background while you play.
