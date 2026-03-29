import json
import os
import re
import sys
import time
import requests
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# ──────────────────────────────────────────────
# WoW path detection
# ──────────────────────────────────────────────

def find_wow_account_dir():
    if sys.platform == "darwin":
        candidates = [
            Path("/Applications/World of Warcraft/_retail_/WTF/Account"),
        ]
    else:
        candidates = [
            Path(r"C:\Program Files (x86)\World of Warcraft\_retail_\WTF\Account"),
            Path(r"C:\Program Files\World of Warcraft\_retail_\WTF\Account"),
        ]
    for path in candidates:
        if path.exists():
            return path
    return None

def pick_account(account_dir):
    accounts = [d for d in account_dir.iterdir() if d.is_dir() and d.name != "SavedVariables"]
    if not accounts:
        return None
    if len(accounts) == 1:
        print(f"Found WoW account: {accounts[0].name}")
        return accounts[0]
    print("\nMultiple WoW accounts found:")
    for i, acc in enumerate(accounts, 1):
        print(f"  {i}. {acc.name}")
    while True:
        try:
            choice = int(input("Select account number: ")) - 1
            return accounts[choice]
        except (ValueError, IndexError):
            print("Invalid choice, try again.")

# ──────────────────────────────────────────────
# First-run setup
# ──────────────────────────────────────────────

def setup():
    print("=" * 40)
    print("  Queue Notifier — First-time Setup")
    print("=" * 40)

    # Locate SavedVariables file
    account_dir = find_wow_account_dir()
    if account_dir:
        account = pick_account(account_dir)
        if account:
            saved_vars = account / "SavedVariables" / "QueueNotifier.lua"
            print(f"\nSavedVariables path:\n  {saved_vars}")
        else:
            saved_vars = None
    else:
        saved_vars = None

    if not saved_vars:
        raw = input("\nCould not auto-detect WoW path.\nPaste the full path to QueueNotifier.lua: ").strip()
        saved_vars = Path(raw)

    # Telegram setup
    print("\n── Telegram Setup ──────────────────────")
    print("1. Open Telegram and message @BotFather")
    print("2. Send /newbot and follow the prompts")
    print("3. Copy the bot token it gives you\n")
    token = input("Paste your Bot Token: ").strip()

    print(f"\nNow send any message to your new bot, then open this URL in a browser:")
    print(f"  https://api.telegram.org/bot{token}/getUpdates")
    print("Look for the 'id' field inside 'chat'.\n")
    chat_id = input("Paste your Chat ID: ").strip()

    # Confirm with a test message
    print("\nSending a test message to confirm everything works...")
    try:
        send_message(token, chat_id, "Queue Notifier is connected! You will be notified when your queue pops.")
        print("Test message sent successfully.")
    except Exception as e:
        print(f"Warning: could not send test message — {e}")
        print("Double-check your token and chat ID, but setup will continue.")

    config = {
        "bot_token": token,
        "chat_id": chat_id,
        "saved_vars_path": str(saved_vars),
    }
    save_config(config)
    print(f"\nConfig saved to {CONFIG_FILE}\n")
    return config

# ──────────────────────────────────────────────
# SavedVariables parsing
# ──────────────────────────────────────────────

def read_last_pop(path):
    try:
        content = Path(path).read_text(encoding="utf-8")
        match = re.search(r'"lastPop"\s*\]\s*=\s*(\d+)', content)
        return int(match.group(1)) if match else None
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading SavedVariables: {e}")
        return None

# ──────────────────────────────────────────────
# Telegram
# ──────────────────────────────────────────────

def send_message(token, chat_id, text):
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    response.raise_for_status()

# ──────────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────────

def main():
    config = load_config()
    if not config:
        config = setup()

    saved_vars = config["saved_vars_path"]
    token = config["bot_token"]
    chat_id = config["chat_id"]

    print(f"Watching: {saved_vars}")
    print("Queue Notifier is running. Press Ctrl+C to stop.\n")

    last_known = read_last_pop(saved_vars)
    print(f"Initial lastPop value: {last_known}\n")

    while True:
        try:
            current = read_last_pop(saved_vars)
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] lastPop = {current}", end="\r")

            if current is not None and current != last_known:
                print(f"\n[{timestamp}] Change detected — sending Telegram notification...")
                try:
                    send_message(token, chat_id, f"Your Arena queue has popped! Accept it!")
                    print(f"[{timestamp}] Notification sent.")
                except Exception as e:
                    print(f"[{timestamp}] Failed to send notification: {e}")
                last_known = current

            time.sleep(2)

        except KeyboardInterrupt:
            print("\nQueue Notifier stopped.")
            break

if __name__ == "__main__":
    main()
