import tkinter as tk
from tkinter import scrolledtext
from kokoro import KPipeline
import soundfile as sf
import os
import threading
import re
import subprocess
from queue import Queue

# Load model
print("Loading model...")
pipeline = KPipeline(lang_code='a')
print("Ready!")

def update_speed_label(value):
    speed_value_label.config(text=f"{float(value):.1f}")

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

    status_label.config(text="Processing...")
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
                status_label.config(text=f"Playing chunk {chunk_num}/{len(chunks)}...")

                # Write and play audio
                temp_file = f'/tmp/output_chunk_{i}.wav'
                sf.write(temp_file, audio, 24000)
                subprocess.run(['afplay', temp_file], check=True)

                # Cleanup
                try:
                    os.remove(temp_file)
                except:
                    pass

            status_label.config(text="Ready")

        # Start both threads
        gen_thread = threading.Thread(target=audio_generator_thread, daemon=True)
        play_thread = threading.Thread(target=audio_player_thread, daemon=True)

        gen_thread.start()
        play_thread.start()

        play_thread.join()  # Wait for playback to complete

    threading.Thread(target=generate_and_play, daemon=True).start()

# GUI
root = tk.Tk()
root.title("Text to Speech")
root.geometry("500x480")

text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15)
text_box.pack(pady=20)

# Speed slider frame
speed_frame = tk.Frame(root)
speed_frame.pack(pady=5)

speed_label = tk.Label(speed_frame, text="Speed:")
speed_label.pack(side=tk.LEFT, padx=(0, 10))

speed_slider = tk.Scale(speed_frame, from_=0.5, to=2.0, resolution=0.1,
                        orient=tk.HORIZONTAL, length=200,
                        command=update_speed_label, showvalue=False)
speed_slider.set(1.5)
speed_slider.pack(side=tk.LEFT)

speed_value_label = tk.Label(speed_frame, text="1.5", width=4)
speed_value_label.pack(side=tk.LEFT, padx=(10, 0))

speak_button = tk.Button(root, text="Speak", command=speak, width=20, height=2)
speak_button.pack(pady=10)

status_label = tk.Label(root, text="Ready")
status_label.pack()

root.mainloop()
