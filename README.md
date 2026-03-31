# QueueNotifier — Installation Guide

## Download

Click the green **Code** button at the top of this page and select **Download ZIP**. Extract the ZIP to a folder of your choice.

---

## Requirements

- World of Warcraft (Retail)
- [Python 3.8+](https://www.python.org/downloads/)
- A Telegram account and/or a Discord server

---

## Step 1 — Set Up Notifications

You can use **Telegram**, **Discord**, or both. At least one is required.

### Telegram

1. Open Telegram and message **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the **bot token** it gives you (e.g. `123456789:ABC-abc_abcd`)
4. Send any message to your new bot
5. Open this URL in a browser (replace `TOKEN` with your token):
   ```
   https://api.telegram.org/botTOKEN/getUpdates
   ```
6. Find the `"id"` field inside `"chat"` — this is your **Chat ID**

> If you see an empty response, wait a minute and try again after sending another message to your bot.

### Discord

1. Open Discord and go to the channel you want to receive notifications in
2. Click **Edit Channel** → **Integrations** → **Webhooks** → **New Webhook**
3. Copy the **Webhook URL**

---

## Step 2 — Install the WoW Addon

From the `addon` folder, copy the `QueueNotifier` folder into your WoW AddOns directory:

**macOS**
```
/Applications/World of Warcraft/_retail_/Interface/AddOns/
```

**Windows**
```
C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\
```

Launch WoW, go to the **AddOns** menu on the character select screen, and enable **Queue Notifier**.

> If WoW flags the addon as out of date, run `/run print(GetBuildInfo())` in-game. It will print something like:
> ```
> 12.0.1 66709 Mar 27 2026 120001
> ```
> Take the **last number** (`120001`) and update the interface number on line 1 of `QueueNotifier.toc`:
> ```
> ## Interface-Retail: 120001
> ```

---

## Step 3 — Run the Companion App

**macOS** — double-click `run_mac.command`
> On first run, right-click → Open to bypass Gatekeeper.

**Windows** — double-click `run_windows.bat`

The app will open a window where you can enter your Telegram and/or Discord credentials. Use the **Send Test** button next to each service to confirm they are working, then click **Save** and **Start**.

Leave the companion app running in the background while you play.
