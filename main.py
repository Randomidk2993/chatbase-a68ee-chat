import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk, ImageSequence
import requests
from io import BytesIO
import time

GIF_URL = "https://media.giphy.com/media/mWzeFtOFcFrDM22VFG/giphy.gif"

def download_gif(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BytesIO(response.content)

class GifWindow:
    def __init__(self, master=None):
        self.master = master or tk.Tk()
        self.master.title("Look at this!")
        self.master.resizable(False, False)

        # ---- REMOVE MINIMIZE/MAXIMIZE BUTTONS (keeps close button) ----
        self.master.attributes('-toolwindow', True)

        # ---- ALWAYS ON TOP ----
        self.master.attributes('-topmost', True)

        # ---- PREVENT MINIMIZE VIA KEYBOARD / TASKBAR ----
        self.master.bind('<Unmap>', self.on_unmap)
        self.master.bind('<Map>', self.on_map)

        # ---- CLOSE PROTOCOL ----
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load GIF
        self.frames = []
        self.durations = []
        gif_data = download_gif(GIF_URL)
        img = Image.open(gif_data)
        for frame in ImageSequence.Iterator(img):
            frame_image = ImageTk.PhotoImage(frame.convert("RGBA"))
            self.frames.append(frame_image)
            self.durations.append(frame.info.get('duration', 100))

        self.frame_index = 0
        self.label = Label(self.master)
        self.label.pack()

        self.animate()

        # Close protection
        self.start_time = time.time()
        self.can_close = False
        self.master.after(10000, self.enable_close)

        # Aggressive topmost enforcement
        self.enforce_topmost()

        windows.append(self)

    def animate(self):
        frame = self.frames[self.frame_index]
        self.label.configure(image=frame)
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.master.after(self.durations[self.frame_index], self.animate)

    def on_unmap(self, event=None):
        """Called when window is hidden/minimized."""
        # If we are being unmapped (hidden) and it's not a legitimate close
        if not self.can_close:
            self.master.after(10, self.restore_window)

    def on_map(self, event=None):
        """Called when window becomes visible."""
        self.master.attributes('-topmost', True)
        self.master.lift()

    def restore_window(self):
        """Force window back to visible and on top."""
        if self.master.state() == 'iconic':
            self.master.deiconify()
        self.master.lift()
        self.master.attributes('-topmost', True)
        self.master.focus_force()

    def enforce_topmost(self):
        """Reapply topmost every 500ms to combat aggressive window managers."""
        self.master.attributes('-topmost', True)
        self.master.lift()
        self.master.after(500, self.enforce_topmost)

    def enable_close(self):
        self.can_close = True
        self.master.title("Look at this! (Can close now)")

    def on_close(self):
        if self.can_close:
            self.master.destroy()
            windows.remove(self)
        else:
            new_root = tk.Toplevel()
            GifWindow(new_root)

windows = []

if __name__ == "__main__":
    root = tk.Tk()
    app = GifWindow(root)
    root.mainloop()
