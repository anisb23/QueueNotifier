import json
import re
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = Path(__file__).parent / "config.json"

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

def find_saved_vars():
    if sys.platform == "darwin":
        account_root = Path("/Applications/World of Warcraft/_retail_/WTF/Account")
    else:
        for base in [
            Path(r"C:\Program Files (x86)\World of Warcraft\_retail_\WTF\Account"),
            Path(r"C:\Program Files\World of Warcraft\_retail_\WTF\Account"),
        ]:
            if base.exists():
                account_root = base
                break
        else:
            return ""

    accounts = [d for d in account_root.iterdir() if d.is_dir() and d.name != "SavedVariables"]
    if not accounts:
        return ""
    return str(accounts[0] / "SavedVariables" / "QueueNotifier.lua")

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
# SavedVariables parsing
# ──────────────────────────────────────────────

def read_last_pop(path):
    try:
        content = Path(path).read_text(encoding="utf-8")
        match = re.search(r'"lastPop"\s*\]\s*=\s*(\d+)', content)
        return int(match.group(1)) if match else None
    except FileNotFoundError:
        return None
    except Exception:
        return None

# ──────────────────────────────────────────────
# File watcher
# ──────────────────────────────────────────────

class SavedVarsHandler(FileSystemEventHandler):
    def __init__(self, saved_vars, token, chat_id, on_notification):
        self.saved_vars = str(Path(saved_vars).resolve())
        self.token = token
        self.chat_id = chat_id
        self.on_notification = on_notification
        self.last_known = read_last_pop(saved_vars)

    def on_modified(self, event):
        if str(Path(event.src_path).resolve()) != self.saved_vars:
            return
        current = read_last_pop(self.saved_vars)
        if current is not None and current != self.last_known:
            self.last_known = current
            timestamp = time.strftime("%H:%M:%S")
            try:
                send_message(self.token, self.chat_id, "Your Solo Shuffle queue has popped! Accept it!")
                self.on_notification(f"[{timestamp}] Notification sent.")
            except Exception as e:
                self.on_notification(f"[{timestamp}] Failed to send: {e}")

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

        pad = {"padx": 10, "pady": 5}

        # Bot Token
        tk.Label(root, text="Telegram Bot Token:").grid(row=0, column=0, sticky="w", **pad)
        self.token_var = tk.StringVar(value=self.config.get("bot_token", ""))
        self.token_entry = tk.Entry(root, textvariable=self.token_var, width=50)
        self.token_entry.grid(row=0, column=1, **pad)

        # Chat ID
        tk.Label(root, text="Telegram Chat ID:").grid(row=1, column=0, sticky="w", **pad)
        self.chat_id_var = tk.StringVar(value=self.config.get("chat_id", ""))
        self.chat_id_entry = tk.Entry(root, textvariable=self.chat_id_var, width=50)
        self.chat_id_entry.grid(row=1, column=1, **pad)

        # SavedVariables path
        tk.Label(root, text="QueueNotifier.lua path:").grid(row=2, column=0, sticky="w", **pad)
        detected = self.config.get("saved_vars_path", "") or find_saved_vars()
        self.path_var = tk.StringVar(value=detected)
        self.path_entry = tk.Entry(root, textvariable=self.path_var, width=50)
        self.path_entry.grid(row=2, column=1, **pad)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.save_btn = tk.Button(btn_frame, text="Save", width=12, command=self.save)
        self.save_btn.pack(side="left", padx=5)

        self.test_btn = tk.Button(btn_frame, text="Send Test", width=12, command=self.send_test)
        self.test_btn.pack(side="left", padx=5)

        self.toggle_btn = tk.Button(btn_frame, text="Start", width=12, command=self.toggle, bg="#4CAF50", fg="white")
        self.toggle_btn.pack(side="left", padx=5)

        # Status
        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = tk.Label(root, textvariable=self.status_var, fg="gray")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(0, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def save(self):
        config = {
            "bot_token": self.token_var.get().strip(),
            "chat_id": self.chat_id_var.get().strip(),
            "saved_vars_path": self.path_var.get().strip(),
        }
        save_config(config)
        self.config = config
        self.set_status("Settings saved.", "green")

    def send_test(self):
        token = self.token_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        if not token or not chat_id:
            messagebox.showwarning("Missing fields", "Please enter your Bot Token and Chat ID first.")
            return
        try:
            send_message(token, chat_id, "Queue Notifier is connected! You will be notified when your Solo Shuffle queue pops.")
            messagebox.showinfo("Success", "Test message sent!")
        except Exception as e:
            messagebox.showerror("Failed", f"Could not send message:\n{e}")

    def toggle(self):
        if self.observer and self.observer.is_alive():
            self.stop_watcher()
        else:
            self.start_watcher()

    def start_watcher(self):
        token = self.token_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        saved_vars = self.path_var.get().strip()

        if not token or not chat_id or not saved_vars:
            messagebox.showwarning("Missing fields", "Please fill in all fields before starting.")
            return

        handler = SavedVarsHandler(saved_vars, token, chat_id, self.set_status)
        self.observer = Observer()
        self.observer.schedule(handler, path=str(Path(saved_vars).parent), recursive=False)
        self.observer.start()

        self.toggle_btn.config(text="Stop", bg="#f44336")
        self.set_status("Running — waiting for queue pop...", "green")

    def stop_watcher(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.toggle_btn.config(text="Start", bg="#4CAF50")
        self.set_status("Stopped", "gray")

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
    root = tk.Tk()
    app = App(root)
    root.mainloop()
