import tkinter as tk
from tkinter import scrolledtext, font, ttk
from kokoro import KPipeline
import soundfile as sf
import os
import threading
import re
import subprocess
from queue import Queue

# Detect system dark mode
def is_dark_mode():
    try:
        result = subprocess.run(
            ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
            capture_output=True,
            text=True
        )
        return 'Dark' in result.stdout
    except:
        return False

# Set colors based on system appearance
DARK_MODE = is_dark_mode()

if DARK_MODE:
    BG_COLOR = "#1E1E1E"
    TEXT_BG = "#2D2D2D"
    TEXT_COLOR = "#FFFFFF"
    SECONDARY_TEXT = "#A0A0A0"
    ACCENT_COLOR = "#0A84FF"
    BUTTON_HOVER = "#0066CC"
    BORDER_COLOR = "#3D3D3D"
else:
    BG_COLOR = "#FFFFFF"
    TEXT_BG = "#F5F5F5"
    TEXT_COLOR = "#000000"
    SECONDARY_TEXT = "#666666"
    ACCENT_COLOR = "#007AFF"
    BUTTON_HOVER = "#0051D5"
    BORDER_COLOR = "#D1D1D6"

# Load model
print("Loading model...")
pipeline = KPipeline(lang_code='a')
print("Ready!")

def filter_long_strings(text):
    """Remove words/strings longer than 20 characters (likely URLs)"""
    words = text.split()
    filtered = []
    for word in words:
        # Check if the word without punctuation is >20 chars
        clean_word = re.sub(r'[^\w]', '', word)
        if len(clean_word) <= 20:
            filtered.append(word)
        else:
            print(f"Filtered out: {word[:30]}...")
    return ' '.join(filtered)

def split_long_line(line, max_length=200):
    """Split a single line that's too long into chunks at sentence boundaries"""
    chunks = []
    current_chunk = ""

    # Split by sentences (periods, exclamation, question marks)
    sentences = re.split(r'([.!?]+\s*)', line)

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        punctuation = sentences[i+1] if i+1 < len(sentences) else ""
        full_sentence = sentence + punctuation

        if len(current_chunk) + len(full_sentence) <= max_length:
            current_chunk += full_sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = full_sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def split_into_chunks(text, max_length=200):
    """Split text into chunks, treating each line/bullet point as separate"""
    chunks = []

    # Split by any newline (single or double) - this preserves line breaks
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # If line is short enough, keep it as one chunk
        if len(line) <= max_length:
            chunks.append(line)
        else:
            # Split long lines by sentences
            line_chunks = split_long_line(line, max_length)
            chunks.extend(line_chunks)

    return chunks

def speak():
    # Get text and preserve newlines
    text = text_box.get("1.0", "end-1c")
    if not text.strip():
        return

    button_canvas.itemconfig(button_text_sub, text="Processing...")
    speed = speed_slider.get()

    def generate_and_play():
        # Filter out long strings (URLs, etc)
        filtered_text = filter_long_strings(text)

        # Split into chunks
        chunks = split_into_chunks(filtered_text)
        print(f"Split into {len(chunks)} chunks")

        audio_queue = Queue()
        stop_flag = threading.Event()

        def audio_generator_thread():
            """Generate audio for all chunks and put in queue"""
            for i, chunk in enumerate(chunks):
                if stop_flag.is_set():
                    break
                print(f"Generating chunk {i+1}/{len(chunks)}: {chunk[:50]}...")

                audio_gen = pipeline(chunk, voice='af_heart', speed=speed)
                for _, _, audio in audio_gen:
                    audio_queue.put((i, audio))
                    break
            audio_queue.put(None)  # Signal completion

        def audio_player_thread():
            """Play audio chunks as they become available"""
            chunk_num = 0
            while True:
                item = audio_queue.get()
                if item is None:
                    break

                i, audio = item
                chunk_num = i + 1
                button_canvas.itemconfig(button_text_sub, text=f"{chunk_num}/{len(chunks)}")

                # Write and play audio
                temp_file = f'/tmp/output_chunk_{i}.wav'
                sf.write(temp_file, audio, 24000)
                subprocess.run(['afplay', temp_file], check=True)

                # Cleanup
                try:
                    os.remove(temp_file)
                except:
                    pass

            button_canvas.itemconfig(button_text_sub, text="Kokoro-82M")

        # Start both threads
        gen_thread = threading.Thread(target=audio_generator_thread, daemon=True)
        play_thread = threading.Thread(target=audio_player_thread, daemon=True)

        gen_thread.start()
        play_thread.start()

        play_thread.join()  # Wait for playback to complete

    threading.Thread(target=generate_and_play, daemon=True).start()

# Custom slider class
class ModernSlider:
    def __init__(self, parent, from_, to, initial_value, callback, value_label=None):
        self.parent = parent
        self.from_ = from_
        self.to = to
        self.value = initial_value
        self.callback = callback
        self.value_label = value_label

        self.canvas = tk.Canvas(parent, width=120, height=20, bg=TEXT_BG, highlightthickness=0)
        self.canvas.pack()

        # Draw beam
        self.beam = self.canvas.create_line(10, 10, 110, 10, fill=BORDER_COLOR, width=2)

        # Draw dot
        x = self.value_to_x(initial_value)
        self.dot = self.canvas.create_oval(x-6, 4, x+6, 16, fill=ACCENT_COLOR, outline="")

        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)

    def value_to_x(self, value):
        return 10 + (value - self.from_) / (self.to - self.from_) * 100

    def x_to_value(self, x):
        if x < 10: x = 10
        if x > 110: x = 110
        return self.from_ + (x - 10) / 100 * (self.to - self.from_)

    def on_click(self, event):
        self.update_value(event.x)

    def on_drag(self, event):
        self.update_value(event.x)

    def on_enter(self, event):
        if self.value_label:
            self.value_label.config(text=f"{self.value:.1f}×")

    def on_leave(self, event):
        if self.value_label:
            self.value_label.config(text="")

    def update_value(self, x):
        self.value = round(self.x_to_value(x), 1)
        new_x = self.value_to_x(self.value)
        self.canvas.coords(self.dot, new_x-6, 4, new_x+6, 16)
        if self.value_label:
            self.value_label.config(text=f"{self.value:.1f}×")
        self.callback(self.value)

    def get(self):
        return self.value

# GUI
root = tk.Tk()
root.title("Text to Speech")
root.geometry("700x600")
root.configure(bg=TEXT_BG)

# Configure scrollbar style
style = ttk.Style()
style.theme_use('default')

if DARK_MODE:
    SCROLLBAR_COLOR = "#505050"
else:
    SCROLLBAR_COLOR = "#C0C0C0"

style.configure("Vertical.TScrollbar",
    background=TEXT_BG,
    troughcolor=TEXT_BG,
    bordercolor=TEXT_BG,
    arrowcolor=SCROLLBAR_COLOR,
    relief="flat",
    borderwidth=0,
    troughrelief="flat"
)

style.map("Vertical.TScrollbar",
    background=[('active', SCROLLBAR_COLOR), ('!active', SCROLLBAR_COLOR)]
)

# Full window text box with scrollbar
text_frame = tk.Frame(root, bg=TEXT_BG)
text_frame.pack(fill=tk.BOTH, expand=True)

text_box = tk.Text(
    text_frame,
    wrap=tk.WORD,
    font=("Helvetica", 14),
    bg=TEXT_BG,
    fg=TEXT_COLOR,
    relief=tk.FLAT,
    borderwidth=0,
    insertbackground=ACCENT_COLOR,
    padx=20,
    pady=20
)
text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_box.yview, style="Vertical.TScrollbar")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_box.config(yscrollcommand=scrollbar.set)

# Keyboard shortcuts
def on_cmd_enter(event):
    speak()
    return "break"  # Prevent default behavior

# Bind cmd+enter to speak
text_box.bind("<Command-Return>", on_cmd_enter)

# Floating controls container (bottom-right)
controls_frame = tk.Frame(root, bg=TEXT_BG)
controls_frame.place(relx=1.0, rely=1.0, x=-30, y=-30, anchor="se")

# Create floating button with canvas
button_canvas = tk.Canvas(controls_frame, width=140, height=80, bg=TEXT_BG, highlightthickness=0)
button_canvas.pack()

def create_rounded_rect(x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1+radius, y1,
        x1+radius, y1,
        x2-radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1+radius,
        x1, y1
    ]
    return button_canvas.create_polygon(points, smooth=True, **kwargs)

button_rect = create_rounded_rect(0, 0, 140, 80, 20, fill=ACCENT_COLOR, outline="")
button_text_main = button_canvas.create_text(70, 30, text="Speak", font=("Helvetica", 18, "bold"), fill="#FFFFFF")
button_text_sub = button_canvas.create_text(70, 55, text="Kokoro-82M", font=("Helvetica", 10), fill="#FFFFFF")

# Speed slider below button (always visible, minimal)
speed_container = tk.Frame(controls_frame, bg=TEXT_BG)
speed_container.pack(pady=(10, 0))

def slider_callback(value):
    pass  # Speed updates handled in ModernSlider

# Value label that appears on hover (below slider)
speed_value_label = tk.Label(speed_container, text="", font=("Helvetica", 9), bg=TEXT_BG, fg=TEXT_COLOR, height=1)

speed_slider = ModernSlider(speed_container, 0.5, 2.0, 1.2, slider_callback, speed_value_label)
speed_value_label.pack()

def on_button_enter(event):
    button_canvas.itemconfig(button_rect, fill=BUTTON_HOVER)

def on_button_leave(event):
    button_canvas.itemconfig(button_rect, fill=ACCENT_COLOR)

def on_button_click(event):
    speak()

button_canvas.bind("<Button-1>", on_button_click)
button_canvas.bind("<Enter>", on_button_enter)
button_canvas.bind("<Leave>", on_button_leave)

# Status updates (shown in button subtitle)
status_label = button_text_sub  # Reference to canvas text item

root.mainloop()
