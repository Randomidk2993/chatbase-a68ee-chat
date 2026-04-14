import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk, ImageSequence
import requests
from io import BytesIO
import time
import re
import sys
import traceback

# ---- CONFIGURE YOUR GIF URL HERE ----
# You can use either:
#   - Giphy page:   https://giphy.com/gifs/things-bra-thechive-cz7hzNqWaIx68
#   - Direct media: https://media.giphy.com/media/cz7hzNqWaIx68/giphy.gif
GIF_INPUT_URL = "https://giphy.com/gifs/things-bra-thechive-cz7hzNqWaIx68"
# -------------------------------------

def get_direct_gif_url(url):
    """Convert a Giphy page URL to direct media URL if needed."""
    # If it's already a direct media URL, return as-is
    if "media.giphy.com/media/" in url and url.endswith("/giphy.gif"):
        return url
    # Extract the ID from a Giphy page URL (e.g., .../gifs/...-ID)
    match = re.search(r'/(?:gifs/)?[^/]+-([a-zA-Z0-9]+)(?:/|$)', url)
    if match:
        gif_id = match.group(1)
        return f"https://media.giphy.com/media/{gif_id}/giphy.gif"
    # Fallback: just return the original URL and hope it's valid
    return url

GIF_URL = get_direct_gif_url(GIF_INPUT_URL)

# Set up error logging
LOG_FILE = "error.log"
def log_error(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def download_gif(url):
    """Download GIF from URL and return BytesIO object."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Verify it's actually an image (not HTML error page)
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            raise ValueError(f"URL did not return an image (got {content_type})")
        return BytesIO(response.content)
    except Exception as e:
        log_error(f"GIF download failed: {e}\nURL: {url}")
        raise

class GifWindow:
    def __init__(self, master=None):
        self.master = master or tk.Tk()
        self.master.title("Look at this!")
        self.master.resizable(False, False)
        self.master.attributes('-topmost', True)

        self.master.bind('<Unmap>', self.on_unmap)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        try:
            # Load GIF
            self.frames = []
            self.durations = []
            gif_data = download_gif(GIF_URL)
            img = Image.open(gif_data)
            for frame in ImageSequence.Iterator(img):
                frame_image = ImageTk.PhotoImage(frame.convert("RGBA"))
                self.frames.append(frame_image)
                self.durations.append(frame.info.get('duration', 100))
        except Exception as e:
            log_error(f"GIF processing failed: {traceback.format_exc()}")
            self.master.destroy()
            return

        self.frame_index = 0
        self.label = Label(self.master)
        self.label.pack()
        self.animate()

        self.start_time = time.time()
        self.can_close = False
        self.master.after(10000, self.enable_close)

        self.enforce_topmost()
        windows.append(self)

    def animate(self):
        try:
            frame = self.frames[self.frame_index]
            self.label.configure(image=frame)
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.master.after(self.durations[self.frame_index], self.animate)
        except Exception:
            pass  # Window might have been destroyed

    def on_unmap(self, event=None):
        if not self.can_close:
            self.master.after(10, self.restore_window)

    def restore_window(self):
        try:
            if self.master.state() == 'iconic':
                self.master.deiconify()
            self.master.lift()
            self.master.attributes('-topmost', True)
            self.master.focus_force()
        except Exception:
            pass

    def enforce_topmost(self):
        try:
            self.master.attributes('-topmost', True)
            self.master.lift()
            self.master.after(500, self.enforce_topmost)
        except Exception:
            pass

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
    try:
        root = tk.Tk()
        app = GifWindow(root)
        root.mainloop()
    except Exception as e:
        log_error(f"Fatal error: {traceback.format_exc()}")
