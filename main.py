import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk, ImageSequence
import requests
from io import BytesIO
import time

# URL of the GIF
GIF_URL = "https://media.giphy.com/media/mWzeFtOFcFrDM22VFG/giphy.gif"

def download_gif(url):
    """Download GIF from URL and return a BytesIO object."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BytesIO(response.content)

class GifWindow:
    def __init__(self, master=None):
        self.master = master or tk.Tk()
        self.master.title("Look at this!")
        self.master.resizable(False, False)

        # ---- ALWAYS ON TOP ----
        self.master.attributes('-topmost', True)

        # ---- PREVENT MINIMIZE ----
        # Bind the Unmap event (triggered when window is minimized)
        self.master.bind('<Unmap>', self.on_minimize_attempt)
        # Also override the window state changes
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load GIF frames
        self.frames = []
        self.durations = []
        gif_data = download_gif(GIF_URL)
        img = Image.open(gif_data)
        for frame in ImageSequence.Iterator(img):
            frame_image = ImageTk.PhotoImage(frame.convert("RGBA"))
            self.frames.append(frame_image)
            duration = frame.info.get('duration', 100)
            self.durations.append(duration)

        self.frame_index = 0
        self.label = Label(self.master)
        self.label.pack()

        self.animate()

        # 10-second close protection
        self.start_time = time.time()
        self.can_close = False
        self.master.after(10000, self.enable_close)

        # Keep reference to avoid garbage collection
        windows.append(self)

    def animate(self):
        """Update label with next frame."""
        frame = self.frames[self.frame_index]
        self.label.configure(image=frame)
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        delay = self.durations[self.frame_index]
        self.master.after(delay, self.animate)

    def on_minimize_attempt(self, event=None):
        """Intercept minimize and immediately restore window."""
        # Only trigger if window is being minimized (state == 'iconic')
        if self.master.state() == 'iconic':
            self.master.deiconify()          # Restore from minimize
            self.master.lift()                # Bring to front
            self.master.attributes('-topmost', True)  # Ensure topmost
        # If it's just an Unmap event not from minimize, do nothing else

    def enable_close(self):
        self.can_close = True
        self.master.title("Look at this! (Can close now)")

    def on_close(self):
        if self.can_close:
            self.master.destroy()
            windows.remove(self)
        else:
            # Spawn a new window when forced closed early
            new_root = tk.Toplevel()
            GifWindow(new_root)

# Global list to keep references to all windows
windows = []

if __name__ == "__main__":
    root = tk.Tk()
    app = GifWindow(root)
    root.mainloop()
