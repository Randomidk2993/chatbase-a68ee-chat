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

        # Disable window close button for the first 10 seconds
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load GIF frames
        self.frames = []
        self.durations = []
        gif_data = download_gif(GIF_URL)
        img = Image.open(gif_data)
        for frame in ImageSequence.Iterator(img):
            frame_image = ImageTk.PhotoImage(frame.convert("RGBA"))
            self.frames.append(frame_image)
            # Duration in milliseconds (default 100ms if missing)
            duration = frame.info.get('duration', 100)
            self.durations.append(duration)

        self.frame_index = 0
        self.label = Label(self.master)
        self.label.pack()

        # Start animation
        self.animate()

        # Record creation time
        self.start_time = time.time()
        self.can_close = False

        # Schedule close permission after 10 seconds
        self.master.after(10000, self.enable_close)

        # Keep track of all windows to prevent garbage collection
        windows.append(self)

    def animate(self):
        """Update the label with the next frame."""
        frame = self.frames[self.frame_index]
        self.label.configure(image=frame)
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        delay = self.durations[self.frame_index]
        self.master.after(delay, self.animate)

    def enable_close(self):
        """Allow the window to be closed normally."""
        self.can_close = True

    def on_close(self):
        """Handle window close attempt."""
        if self.can_close:
            self.master.destroy()
            windows.remove(self)
        else:
            # Spawn a new window
            new_root = tk.Toplevel()
            GifWindow(new_root)

# Global list to keep references to windows
windows = []

if __name__ == "__main__":
    root = tk.Tk()
    app = GifWindow(root)
    root.mainloop()
