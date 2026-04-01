import json
import os
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

import requests
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

CONFIG_FILE = Path(__file__).parent / "config.json"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# ──────────────────────────────────────────────
# WoW path detection
# ──────────────────────────────────────────────

def find_screenshots_path():
    if sys.platform == "darwin":
        path = Path("/Applications/World of Warcraft/_retail_/Screenshots")
        return str(path) if path.exists() else ""
    for base in [
        Path(r"C:\Program Files (x86)\World of Warcraft\_retail_\Screenshots"),
        Path(r"C:\Program Files\World of Warcraft\_retail_\Screenshots"),
    ]:
        if base.exists():
            return str(base)
    return ""

# ──────────────────────────────────────────────
# Notifications
# ──────────────────────────────────────────────

def send_telegram(token, chat_id, text):
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    response.raise_for_status()

def send_discord(webhook_url, text):
    response = requests.post(
        webhook_url,
        json={"content": text},
        timeout=10,
    )
    response.raise_for_status()

def send_notifications(config, text):
    errors = []
    token = config.get("bot_token", "").strip()
    chat_id = config.get("chat_id", "").strip()
    webhook_url = config.get("discord_webhook", "").strip()

    if token and chat_id:
        try:
            send_telegram(token, chat_id, text)
        except Exception as e:
            errors.append(f"Telegram: {e}")

    if webhook_url:
        try:
            send_discord(webhook_url, text)
        except Exception as e:
            errors.append(f"Discord: {e}")

    if errors:
        raise Exception(" | ".join(errors))

# ──────────────────────────────────────────────
# Screenshot watcher
# ──────────────────────────────────────────────

class ScreenshotHandler(PatternMatchingEventHandler):
    def __init__(self, config, on_notification):
        super().__init__(patterns=["*.tga"], ignore_directories=True, case_sensitive=False)
        self.config = config
        self.on_notification = on_notification

    def on_created(self, event):
        log("Queue pop detected — sending notification...")
        try:
            send_notifications(self.config, "Your Solo Shuffle queue has popped! Accept it!")
            log("Notification sent successfully.")
            self.on_notification(f"[{time.strftime('%H:%M:%S')}] Notification sent.")
        except Exception as e:
            log(f"Failed to send notification: {e}")
            self.on_notification(f"[{time.strftime('%H:%M:%S')}] Failed to send: {e}")
        try:
            os.remove(event.src_path)
            log("Screenshot cleaned up.")
        except Exception:
            pass

# ──────────────────────────────────────────────
# UI
# ──────────────────────────────────────────────

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Queue Notifier")
        self.root.resizable(False, False)

        self.observer = None
        self.config = load_config()

        pad = {"padx": 10, "pady": 4}

        # ── Telegram ──────────────────────────
        telegram_frame = tk.LabelFrame(root, text="Telegram", padx=8, pady=6)
        telegram_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 4))

        tk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky="w")
        self.token_var = tk.StringVar(value=self.config.get("bot_token", ""))
        tk.Entry(telegram_frame, textvariable=self.token_var, width=50).grid(row=0, column=1, padx=(8, 0), pady=3)

        tk.Label(telegram_frame, text="Chat ID:").grid(row=1, column=0, sticky="w")
        self.chat_id_var = tk.StringVar(value=self.config.get("chat_id", ""))
        tk.Entry(telegram_frame, textvariable=self.chat_id_var, width=50).grid(row=1, column=1, padx=(8, 0), pady=3)

        self.test_telegram_btn = tk.Button(telegram_frame, text="Send Test", command=self.test_telegram)
        self.test_telegram_btn.grid(row=2, column=1, sticky="e", pady=(4, 0))

        # ── Discord ───────────────────────────
        discord_frame = tk.LabelFrame(root, text="Discord", padx=8, pady=6)
        discord_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=4)

        tk.Label(discord_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
        self.discord_var = tk.StringVar(value=self.config.get("discord_webhook", ""))
        tk.Entry(discord_frame, textvariable=self.discord_var, width=50).grid(row=0, column=1, padx=(8, 0), pady=3)

        self.test_discord_btn = tk.Button(discord_frame, text="Send Test", command=self.test_discord)
        self.test_discord_btn.grid(row=1, column=1, sticky="e", pady=(4, 0))

        # ── WoW Path ──────────────────────────
        tk.Label(root, text="WoW Screenshots path:").grid(row=2, column=0, sticky="w", **pad)
        detected = self.config.get("screenshots_path", "") or find_screenshots_path()
        self.path_var = tk.StringVar(value=detected)
        tk.Entry(root, textvariable=self.path_var, width=50).grid(row=2, column=1, **pad)

        # ── Buttons ───────────────────────────
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="Save", width=12, command=self.save).pack(side="left", padx=5)

        self.toggle_btn = tk.Button(btn_frame, text="Start", width=12, command=self.toggle, bg="#4CAF50", fg="white")
        self.toggle_btn.pack(side="left", padx=5)

        # ── Warning & Status ──────────────────
        self.warning_var = tk.StringVar()
        tk.Label(root, textvariable=self.warning_var, fg="orange").grid(row=4, column=0, columnspan=2)

        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = tk.Label(root, textvariable=self.status_var, fg="gray")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        for var in (self.token_var, self.chat_id_var, self.discord_var, self.path_var):
            var.trace_add("write", lambda *_: self.validate_fields())
        self.validate_fields()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def validate_fields(self):
        has_telegram = bool(self.token_var.get().strip() and self.chat_id_var.get().strip())
        has_discord = bool(self.discord_var.get().strip())
        has_path = bool(self.path_var.get().strip())

        if not has_path:
            self.toggle_btn.config(state="disabled")
            self.warning_var.set("Please enter the WoW Screenshots path.")
        elif not has_telegram and not has_discord:
            self.toggle_btn.config(state="disabled")
            self.warning_var.set("Please configure at least one notification service.")
        else:
            self.toggle_btn.config(state="normal")
            self.warning_var.set("")

    def save(self):
        config = {
            "bot_token": self.token_var.get().strip(),
            "chat_id": self.chat_id_var.get().strip(),
            "discord_webhook": self.discord_var.get().strip(),
            "screenshots_path": self.path_var.get().strip(),
        }
        save_config(config)
        self.config = config
        log("Settings saved.")
        self.set_status("Settings saved.", "green")

    def test_telegram(self):
        token = self.token_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        if not token or not chat_id:
            messagebox.showwarning("Missing fields", "Please enter your Telegram Bot Token and Chat ID.")
            return
        try:
            send_telegram(token, chat_id, "Queue Notifier is connected! You will be notified when your Solo Shuffle queue pops.")
            messagebox.showinfo("Telegram", "Test message sent successfully!")
        except Exception as e:
            messagebox.showerror("Telegram", f"Could not send message:\n{e}")

    def test_discord(self):
        webhook_url = self.discord_var.get().strip()
        if not webhook_url:
            messagebox.showwarning("Missing fields", "Please enter your Discord Webhook URL.")
            return
        try:
            send_discord(webhook_url, "Queue Notifier is connected! You will be notified when your Solo Shuffle queue pops.")
            messagebox.showinfo("Discord", "Test message sent successfully!")
        except Exception as e:
            messagebox.showerror("Discord", f"Could not send message:\n{e}")

    def toggle(self):
        if self.observer and self.observer.is_alive():
            self.stop_watcher()
        else:
            self.start_watcher()

    def start_watcher(self):
        screenshots_path = self.path_var.get().strip()
        Path(screenshots_path).mkdir(parents=True, exist_ok=True)

        current_config = {
            "bot_token": self.token_var.get().strip(),
            "chat_id": self.chat_id_var.get().strip(),
            "discord_webhook": self.discord_var.get().strip(),
            "screenshots_path": screenshots_path,
        }

        handler = ScreenshotHandler(current_config, self.set_status)
        self.observer = Observer()
        self.observer.schedule(handler, path=screenshots_path, recursive=False)
        self.observer.start()

        self.toggle_btn.config(text="Stop", bg="#f44336")
        self.set_status("Running — waiting for queue pop...", "green")
        log(f"Watcher started. Monitoring: {screenshots_path}")

        self._heartbeat_stop = threading.Event()
        threading.Thread(target=self._heartbeat, daemon=True).start()

    def _heartbeat(self):
        while not self._heartbeat_stop.wait(60):
            log("Still running — waiting for queue pop...")

    def stop_watcher(self):
        if hasattr(self, "_heartbeat_stop"):
            self._heartbeat_stop.set()
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.toggle_btn.config(text="Start", bg="#4CAF50")
        self.set_status("Stopped", "gray")
        log("Watcher stopped.")

    def set_status(self, msg, color="black"):
        self.status_var.set(msg)
        self.status_label.config(fg=color)

    def on_close(self):
        self.stop_watcher()
        self.root.destroy()

# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  Queue Notifier")
    print("=" * 50)
    print()
    print("  !! Do not close this window !!")
    print("  It must stay open while you play.")
    print("  Use the Queue Notifier window to")
    print("  configure your settings and start/stop.")
    print()
    log("Starting up...")

    root = tk.Tk()
    app = App(root)
    root.mainloop()

    log("Application closed.")
