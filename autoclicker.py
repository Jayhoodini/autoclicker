import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import threading
import keyboard  # Added for global hotkey

# Set pyautogui pause to reduce CPU usage
pyautogui.PAUSE = 0.01

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("300x350")
        self.root.resizable(False, False)

        # State variables
        self.clicking = False
        self.mouse_button = tk.StringVar(value="left")
        self.click_type = tk.StringVar(value="single")
        self.hotkey = "F8"
        self.awaiting_hotkey = False

        # GUI Elements
        tk.Label(root, text="Auto Clicker", font=("Arial", 14, "bold")).pack(pady=10)

        # Interval Entry
        tk.Label(root, text="Click Interval (ms):").pack()
        self.interval_entry = tk.Entry(root, width=10)
        self.interval_entry.insert(0, "100")
        self.interval_entry.pack()

        # Mouse Button Selection
        tk.Label(root, text="Mouse Button:").pack()
        tk.Radiobutton(root, text="Left", variable=self.mouse_button, value="left").pack()
        tk.Radiobutton(root, text="Right", variable=self.mouse_button, value="right").pack()

        # Click Type Selection
        tk.Label(root, text="Click Type:").pack()
        tk.Radiobutton(root, text="Single Click", variable=self.click_type, value="single").pack()
        tk.Radiobutton(root, text="Double Click", variable=self.click_type, value="double").pack()

        # Hotkey Button
        self.hotkey_button = tk.Button(root, text=f"Hotkey: {self.hotkey}", command=self.change_hotkey)
        self.hotkey_button.pack(pady=5)

        # Toggle Button
        self.toggle_button = tk.Button(root, text="Start", command=self.toggle_clicking, bg="green", fg="white")
        self.toggle_button.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(root, text="Status: Stopped", fg="red")
        self.status_label.pack(pady=10)

        # Register hotkey
        self.register_hotkey()

    def register_hotkey(self):
        try:
            keyboard.clear_all_hotkeys()
        except Exception as e:
            self.status_label.config(text=f"Hotkey clear error", fg="orange")
        try:
            keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
        except Exception as e:
            self.status_label.config(text=f"Hotkey set error", fg="orange")

    def validate_interval(self):
        try:
            interval = float(self.interval_entry.get())
            if interval < 1:
                messagebox.showerror("Error", "Interval must be at least 1 ms")
                return None
            return interval / 1000  # Convert to seconds
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return None

    def clicker(self):
        while self.clicking:
            interval = self.validate_interval()
            if interval is None:
                self.stop_clicking()
                return
            if self.click_type.get() == "single":
                pyautogui.click(button=self.mouse_button.get())
            else:
                pyautogui.doubleClick(button=self.mouse_button.get())
            time.sleep(interval)

    def toggle_clicking(self):
        if not self.clicking:
            interval = self.validate_interval()
            if interval is None:
                return
            self.clicking = True
            self.toggle_button.config(text="Stop", bg="red")
            self.status_label.config(text="Status: Clicking", fg="green")
            threading.Thread(target=self.clicker, daemon=True).start()
        else:
            self.stop_clicking()

    def stop_clicking(self):
        self.clicking = False
        self.toggle_button.config(text="Start", bg="green")
        self.status_label.config(text="Status: Stopped", fg="red")

    def change_hotkey(self):
        self.status_label.config(text="Press a key for hotkey...")
        self.awaiting_hotkey = True
        self.root.bind('<Key>', self.set_hotkey)

    def set_hotkey(self, event):
        if self.awaiting_hotkey:
            self.hotkey = event.keysym
            self.hotkey_button.config(text=f"Hotkey: {self.hotkey}")
            self.status_label.config(text=f"Hotkey set to: {self.hotkey}", fg="blue")
            self.root.unbind('<Key>')
            self.awaiting_hotkey = False
            self.register_hotkey()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    try:
        root.mainloop()
    finally:
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass